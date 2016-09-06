import logging

from django.contrib.auth.models import User
from django.conf.urls import url
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.db import IntegrityError
from django.http import Http404

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, ApiKeyAuthentication, MultiAuthentication

from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.serializers import Serializer
from tastypie.exceptions import BadRequest
from tastypie_validators import CustomFormValidation

from guardian_auth import GuardianAuthorization
from haystack.query import SearchQuerySet

from freeform_data.models import Organization, UserProfile, Course, Problem, Essay, EssayGrade, Membership, UserRoles

from collections import Iterator
from throttle import UserAccessThrottle
from forms import ProblemForm, EssayForm, EssayGradeForm, UserForm

from django.forms.util import ErrorDict

from allauth.account.forms import SignupForm
from allauth.account.views import complete_signup

log = logging.getLogger(__name__)


class SessionAuthentication(Authentication):
    """
    Override session auth to always return the auth status
    """
    def is_authenticated(self, request, **kwargs):
        """
        Checks to make sure the user is logged in & has a Django session.
        """
        return request.user.is_authenticated()

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.
        This implementation returns the user's username.
        """
        return request.user.username

def default_authorization():
    """
    Used to ensure that changing authorization can be done on a sitewide level easily.
    """
    return GuardianAuthorization()

def default_authentication():
    """
    Ensures that authentication can easily be changed on a sitewide level.
    """
    return MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication())

def default_serialization():
    """
    Current serialization formats.  HTML is not supported for now.
    """
    return Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'html', 'plist'])

def default_throttling():
    """
    Default throttling for models.  Currently only affects essay model.
    """
    return UserAccessThrottle(throttle_at=settings.THROTTLE_AT, timeframe=settings.THROTTLE_TIMEFRAME, expiration= settings.THROTTLE_EXPIRATION)

def run_search(request,obj):
    """
    Runs a search via haystack.
    request - user search request object
    obj - the model for which search is being done
    """
    sqs = SearchQuerySet().models(obj).load_all().auto_query(request.GET.get('q', ''))
    paginator = Paginator(sqs, 20)

    try:
        page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
        raise Http404("Sorry, no results on that page.")

    return page.object_list

class MockQuerySet(Iterator):
    """
    Mock a query set so that it can be used with default authorization
    """
    def __init__(self, model,data):
        """
        model - a model class
        data - list of data to hold in the mock query set
        """
        self.data = data
        self.model = model
        self.current_elem = 0

    def next(self):
        """
        Fetches the next element in the mock query set
        """
        if self.current_elem>=len(self.data):
            self.current_elem=0
            raise StopIteration
        dat = self.data[self.current_elem]
        self.current_elem+=1
        return dat

class SearchModelResource(ModelResource):
    """
    Extends model resource to add search capabilities
    """
    def prepend_urls(self):
        """
        Adds in a search url for each model that accepts query terms and pages.
        """
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
            ]

    def get_search(self, request, **kwargs):
        """
        Gets search results for each of the models that inherit from this class
        request - user request object
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        #Run search via haystack and get list of objects
        object_list = run_search(request,self._meta.model_type)
        objects = []

        #Create bundle and authorization
        auth = default_authorization()
        bundle = None

        #Convert search result list into a list of django models
        object_list = [result.object for result in object_list if result is not None]

        #If there is more than one object, then apply authorization limits to the list
        if len(object_list)>0:
            #Mock a bundle, needed to apply auth limits
            bundle = self.build_bundle(obj=object_list[0], request=request)
            bundle = self.full_dehydrate(bundle)

            #Apply authorization limits via auth object that we previously created
            object_list = auth.read_list(MockQuerySet(self._meta.model_type, object_list),bundle)

        for result in object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
            }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

class CreateUserResource(ModelResource):
    """
    Creates a user with the specified username and password.  This is needed because of permissions restrictions
    on the normal user resource.
    """
    class Meta:
        allowed_methods = ['post']
        object_class = User
        #No authentication for create user, or authorization.  Anyone can create.
        authentication = Authentication()
        authorization = Authorization()
        fields = ['username', 'email']
        resource_name = "createuser"
        always_return_data = True
        throttle = default_throttling()

    def obj_create(self, bundle, **kwargs):
        #Validate that the needed fields exist
        validator = CustomFormValidation(form_class=UserForm, model_type=self._meta.resource_name)
        errors = validator.is_valid(bundle)
        if isinstance(errors, ErrorDict):
            raise BadRequest(errors.as_text())
        #Extract needed fields
        username, password, email = bundle.data['username'], bundle.data['password'], bundle.data['email']
        data_dict = {'username' : username, 'email' : email, 'password' : password, 'password1' : password, 'password2' : password}
        #Pass the fields to django-allauth.  We want to use its email verification setup.
        signup_form = SignupForm()
        signup_form.cleaned_data = data_dict
        try:
            try:
                user = signup_form.save(bundle.request)
                profile, created = UserProfile.objects.get_or_create(user=user)
            except AssertionError:
                #If this fails, the user has a non-unique email address.
                user = User.objects.get(username=username)
                user.delete()
                raise BadRequest("Email address has already been used, try another.")

            #Need this so that the object is added to the bundle and exists during the dehydrate cycle.
            html = complete_signup(bundle.request, user, "")
            bundle.obj = user
        except IntegrityError:
            raise BadRequest("Username is already taken, try another.")

        return bundle

    def dehydrate(self, bundle):
        username = bundle.data.get('username', None)
        if username is not None:
            user = User.objects.get(username=username)
            api_key = user.api_key
            bundle.data['api_key'] = api_key.key
        return bundle

class OrganizationResource(SearchModelResource):
    """
    Preserves appropriate many to many relationships, and encapsulates the Organization model.
    """
    courses = fields.ToManyField('freeform_data.api.CourseResource', 'course_set', null=True)
    essays = fields.ToManyField('freeform_data.api.EssayResource', 'essay_set', null=True)
    #This maps the organization users to the users model via membership
    user_query = lambda bundle: bundle.obj.users.through.objects.all() or bundle.obj.users
    users = fields.ToManyField("freeform_data.api.MembershipResource", attribute=user_query, null=True)
    #Also show members in the organization (useful for getting role)
    memberships = fields.ToManyField("freeform_data.api.MembershipResource", 'membership_set', null=True)
    class Meta:
        queryset = Organization.objects.all()
        resource_name = 'organization'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = Organization
        throttle = default_throttling()

    def obj_create(self, bundle, **kwargs):
        bundle = super(OrganizationResource, self).obj_create(bundle)
        return bundle

    def save_m2m(self,bundle):
        """
        Save_m2m saves many to many models.  This hack adds a membership object, which is needed, as membership
        is the relation through which organization is connected to user.
        """
        add_membership(bundle.request.user, bundle.obj)
        bundle.obj.save()

    def dehydrate_users(self, bundle):
        """
        Tastypie will currently show memberships instead of users due to the through relation.
        This hacks the relation to show users.
        """
        resource_uris = []
        user_resource = UserResource()
        if bundle.data.get('users'):
            l_users = bundle.obj.users.all()
            for l_user in l_users:
                resource_uris.append(user_resource.get_resource_uri(bundle_or_obj=l_user))
        return resource_uris

class UserProfileResource(SearchModelResource):
    """
    Encapsulates the UserProfile module
    """
    user = fields.ToOneField('freeform_data.api.UserResource', 'user', related_name='userprofile')
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'userprofile'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = UserProfile
        excludes = ['throttle_at']
        throttle = default_throttling()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(UserProfileResource, self).obj_create(bundle,user=bundle.request.user)

class UserResource(SearchModelResource):
    """
    Encapsulates the User Model
    """
    essaygrades = fields.ToManyField('freeform_data.api.EssayGradeResource', 'essaygrade_set', null=True, related_name='user')
    essays = fields.ToManyField('freeform_data.api.EssayResource', 'essay_set', null=True, related_name='user')
    courses = fields.ToManyField('freeform_data.api.CourseResource', 'course_set', null=True)
    userprofile = fields.ToOneField('freeform_data.api.UserProfileResource', 'userprofile', related_name='user')
    organizations = fields.ToManyField('freeform_data.api.OrganizationResource', 'organization_set', null=True)
    memberships = fields.ToManyField("freeform_data.api.MembershipResource", 'membership_set', null=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = User
        excludes = ['password']
        throttle = default_throttling()

    def obj_create(self, bundle, **kwargs):
        return super(UserResource, self).obj_create(bundle)

    def dehydrate(self, bundle):
        bundle.data['api_key'] = bundle.obj.api_key.key
        return bundle

class MembershipResource(SearchModelResource):
    """
    Encapsulates the Membership Model
    """
    user = fields.ToOneField('freeform_data.api.UserResource', 'user')
    organization = fields.ToOneField('freeform_data.api.OrganizationResource', 'organization')
    class Meta:
        queryset = Membership.objects.all()
        resource_name = 'membership'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = Membership
        throttle = default_throttling()

    def obj_create(self, bundle, request=None, **kwargs):
        return super(MembershipResource, self).obj_create(bundle,user=bundle.request.user)

class CourseResource(SearchModelResource):
    """
    Encapsulates the Course Model
    """
    organizations = fields.ToManyField(OrganizationResource, 'organizations', null=True)
    users = fields.ToManyField(UserResource, 'users', null=True)
    problems = fields.ToManyField('freeform_data.api.ProblemResource', 'problem_set', null=True)
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = Course
        throttle = default_throttling()

    def obj_create(self, bundle, **kwargs):
        return super(CourseResource, self).obj_create(bundle, user=bundle.request.user)

class ProblemResource(SearchModelResource):
    """
    Encapsulates the problem Model
    """
    essays = fields.ToManyField('freeform_data.api.EssayResource', 'essay_set', null=True, related_name='problem')
    courses = fields.ToManyField('freeform_data.api.CourseResource', 'courses')
    class Meta:
        queryset = Problem.objects.all()
        resource_name = 'problem'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = Problem
        throttle = default_throttling()
        validation = CustomFormValidation(form_class=ProblemForm, model_type=resource_name)

    def obj_create(self, bundle, **kwargs):
        return super(ProblemResource, self).obj_create(bundle)

class EssayResource(SearchModelResource):
    """
    Encapsulates the essay Model
    """
    essaygrades = fields.ToManyField('freeform_data.api.EssayGradeResource', 'essaygrade_set', null=True, related_name='essay')
    user = fields.ToOneField(UserResource, 'user', null=True)
    organization = fields.ToOneField(OrganizationResource, 'organization', null=True)
    problem = fields.ToOneField(ProblemResource, 'problem')
    class Meta:
        queryset = Essay.objects.all()
        resource_name = 'essay'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = Essay
        throttle = default_throttling()
        validation = CustomFormValidation(form_class=EssayForm, model_type=resource_name)

    def obj_create(self, bundle, **kwargs):
        bundle = super(EssayResource, self).obj_create(bundle, user=bundle.request.user)
        bundle.obj.user = bundle.request.user
        bundle.obj.save()
        return bundle

class EssayGradeResource(SearchModelResource):
    """
    Encapsulates the EssayGrade Model
    """
    user = fields.ToOneField(UserResource, 'user', null=True)
    essay = fields.ToOneField(EssayResource, 'essay')
    class Meta:
        queryset = EssayGrade.objects.all()
        resource_name = 'essaygrade'

        serializer = default_serialization()
        authorization= default_authorization()
        authentication = default_authentication()
        always_return_data = True
        model_type = EssayGrade
        throttle = default_throttling()
        validation = CustomFormValidation(form_class=EssayGradeForm, model_type=resource_name)

    def obj_create(self, bundle, **kwargs):
        bundle = super(EssayGradeResource, self).obj_create(bundle, user=bundle.request.user)
        bundle.obj.user = bundle.request.user
        bundle.obj.save()
        return bundle

def add_membership(user,organization):
    """
    Adds a membership object.  Required because membership defines the relation between user and organization,
    and tastypie does not automatically create through relations.
    """
    users = organization.users.all()
    membership_count = Membership.objects.filter(user=user).count()
    if membership_count>=settings.MEMBERSHIP_LIMIT:
        error_message = "All users, including user {0} can only have a maximum of 1 organizations.  This will hopefully be fixed in a future release.".format(user)
        log.info(error_message)
        raise BadRequest(error_message)
    membership = Membership(
        user = user,
        organization = organization,
    )
    if users.count()==0:
        #If a user is the first one in an organization, make them the administrator.
        membership.role = UserRoles.administrator
        membership.save()
    else:
        membership.role = UserRoles.student
    membership.save()

