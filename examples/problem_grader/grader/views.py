from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext, ugettext_lazy as _
from django.forms import EmailField
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import logging
import json
import rubric_functions
import helpers

log = logging.getLogger(__name__)

class UserCreationEmailForm(UserCreationForm):
    email = EmailField(label=_("Email Address"), max_length=30,
                                help_text=_("Required. 30 characters or fewer. Letters, digits and "
                                            "@/./+/-/_ only."),
                                error_messages={
                                    'invalid': _("This value may contain only letters, numbers and "
                                                 "@/./+/-/_ characters.")})
    def save(self, commit=True):
        user = super(UserCreationEmailForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


def register(request):
    """
    Register a new user for a given request
    """
    if request.method == 'POST':
        form = UserCreationEmailForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/grader/")
    else:
        form = UserCreationEmailForm()
    return render_to_response("registration/register.html", RequestContext(request,{
        'form': form,
        }))

def index(request):
    """
    Index page for the site.
    """
    return render_to_response("index.html",RequestContext(request))

#Available types of actions
action_types = ["update", "delete", "get", "post"]

@login_required
def action(request):
    """
    Main handler function for actions.  Needs to be broken up down the line.
    """

    #Support get or post requests
    if request.method == 'POST':
        args = request.POST
    else:
        args = request.GET

    #Action is the type of action to do (see action_types above)
    action = args.get('action', 'get')
    #Model is the model to perform the given action on(ie 'organization')
    model = args.get('model', None)
    #If the action is on a per-instance level (ie delete and update), then get the id to perform the action on.
    id = args.get('id', None)

    #Grab the user
    user = request.user
    #Data is used when posting and updating
    data = args.get('data', None)

    #Data might be in json format, but it might not.  support both
    try:
        data = json.loads(data)
    except:
        pass

    #Check to see if the action is valid.
    if action is None or action not in action_types:
        error = "Action cannot be None, and must be a string in action_types: {0}".format(action_types)
        log.info(error)
        raise TypeError(error)

    #Define a base rubric
    rubric = {'options' : []}
    #If we are posting a problem, then there is additional processing to do before we can submit to the API
    if action=="post" and model=="problem":
        #Grab the rubric for later.
        rubric = data['rubric'].copy()
        #Add in two needed fields (the api requires them)
        data.update({
            'max_target_scores' : [1 for i in xrange(0,len(data['rubric']['options']))],
            'courses' : [helpers.construct_related_uri(data['course'], 'course')]
        })
        #Remove these keys (posting to the api will fail if they are still in)
        del data['rubric']
        del data['course']

    #We need to convert the integer id into a resource uri before posting to the API
    if action=="post" and model=="essay":
        data['problem'] = helpers.construct_related_uri(data['problem'], 'problem')

    #We need to convert the integer id into a resource uri before posting to the API
    if action=="post" and model=="essaygrade":
        data['essay'] = helpers.construct_related_uri(data['essay'], 'essay')

    #If we are deleting a problem, delete its local model uri
    if action=="delete" and model=="problem":
        rubric_functions.delete_rubric_data(id)

    #Setup all slumber models for the current user
    slumber_models = helpers.setup_slumber_models(user)

    #Check to see if the user requested model exists at the API endpoint
    if model not in slumber_models:
        error = "Invalid model specified :{0} .  Model does not appear to exist in list: {1}".format(model, slumber_models.keys())
        log.info(error)
        raise Exception(error)

    try:
        #Try to see if we can perform the given action on the given model
        slumber_data = slumber_models[model].action(action,id=id,data=data)
    except Exception as inst:
        #If we cannot, log the error information from slumber.  Will likely contain the error message recieved from the api
        error_message = "Could not perform action {action} on model type {model} with id {id} and data {data}.".format(action=action, model=model, id=id, data=data)
        error_information = "Recieved the following from the server.  Args: {args} , response: {response}, content: {content}".format(args=inst.args, response=inst.response, content=inst.content)
        log.error(error_message)
        log.error(error_information)
        raise

    #If we have posted a problem, we need to create a local rubric object to store our rubric (the api does not do this)
    if action=="post" and model=="problem":
        problem_id = slumber_data['id']
        rubric['problem_id'] = problem_id
        #Create the rubric object
        rubric_functions.create_rubric_objects(rubric, request)

    #Append rubric to problem and essay objects
    if (action in ["get", "post"] and model=="problem") or (action=="get" and model=="essay"):
        if isinstance(slumber_data,list):
            for i in xrange(0,len(slumber_data)):
                    slumber_data[i]['rubric'] = helpers.get_rubric_data(model, slumber_data[i])
        else:
            slumber_data['rubric'] = helpers.get_rubric_data(model, slumber_data)

    #append essaygrades to essay objects
    if action=="get" and model=="essay":
        essaygrades = slumber_models['essaygrade'].action('get')
        if isinstance(slumber_data,list):
            for i in xrange(0,len(slumber_data)):
                slumber_data[i]['essaygrades_full'] = helpers.get_essaygrade_data(slumber_data[i], essaygrades)
        else:
            slumber_data['essaygrades_full'] = helpers.get_essaygrade_data(slumber_data, essaygrades)

    json_data = json.dumps(slumber_data)
    return HttpResponse(json_data)

@login_required
def course(request):
    """
    Render the page for courses
    """
    return render_to_response('course.html', RequestContext(request, {'model' : 'course', 'api_url' : "/grader/action"}))

@login_required
def problem(request):
    """
    Render the page for problems.  This can take the argument course_id.
    """

    #Accept either get or post requests
    if request.method == 'POST':
        args = request.POST
    else:
        args = request.GET

    #If provided, get the course id argument
    matching_course_id = args.get('course_id', -1)
    match_course = False
    course_name = None

    #If a course to match problems to has been specified, grab the matching course and return it
    if matching_course_id!= -1:
        match_course = True
        user = request.user
        slumber_models = helpers.setup_slumber_models(user)
        course_object = slumber_models['course'].action('get',id=matching_course_id, data=None)
        course_name = course_object['course_name']

    matching_course_id = str(matching_course_id)


    return render_to_response('problem.html', RequestContext(request, {'model' : 'problem',
                                                                       'api_url' : "/grader/action",
                                                                       'matching_course_id' : matching_course_id,
                                                                       'match_course' : match_course,
                                                                       'course_name' : course_name,
    })
    )

@login_required
def write_essays(request):
    """
    Render the page for writing essays
    """
    return render_to_response('write_essay.html', RequestContext(request, {'api_url' : "/grader/action", 'model' : 'essay',}))

@login_required
def grade_essays(request):
    """
    Render the page for grading essays
    """
    return render_to_response('grade_essay.html', RequestContext(request, {'api_url' : "/grader/action", 'model' : 'essaygrade',}))


