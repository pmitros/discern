from django.db import models
from django.contrib.auth.models import User, Group, Permission
from tastypie.models import create_api_key
import json
from django.db.models.signals import pre_delete, pre_save, post_save, post_delete
from request_provider.signals import get_request
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import SiteProfileNotAvailable
from guardian.shortcuts import assign_perm

import logging
log=logging.getLogger(__name__)

#CLASSES THAT WRAP CONSTANTS

class UserRoles(object):
    student = "student"
    teacher = "teacher"
    administrator = "administrator"
    grader = "grader"
    creator = "creator"

class EssayTypes(object):
    test = "test"
    train = "train"

class GraderTypes(object):
    machine = "ML"
    instructor = "IN"
    peer = "PE"
    self = "SE"

ESSAY_TYPES = (
    (EssayTypes.test, EssayTypes.test),
    (EssayTypes.train, EssayTypes.train)
)

GRADER_TYPES = (
    (GraderTypes.machine, GraderTypes.machine),
    (GraderTypes.instructor, GraderTypes.instructor),
    (GraderTypes.peer, GraderTypes.peer),
    (GraderTypes.self, GraderTypes.self),
)


PERMISSIONS = ["view", "add", "delete", "change"]
PERMISSION_MODELS = ["organization", "membership", "userprofile", "course", "problem", "essay", "essaygrade"]

#MODELS

class Organization(models.Model):
    #TODO: Add in address info, etc later on
    organization_size = models.IntegerField(default=0)
    organization_name = models.TextField(default="")
    #TODO: Add in billing details, etc later, along with rules on when to ask
    premium_service_subscriptions = models.TextField(default=json.dumps([]))
    #Each organization can have many users, and a user can be in multiple organizations
    users = models.ManyToManyField(User, blank=True,null=True, through="freeform_data.Membership")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_organization", "Can view organization"),
        )

class Membership(models.Model):
    role = models.CharField(max_length=20, default=UserRoles.student)
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(User)

    class Meta:
        permissions = (
            ("view_membership", "Can view membership"),
        )

    def save(self, *args, **kwargs):
        members_count = Membership.objects.filter(user = self.user).exclude(id=self.id).count()
        if members_count>=settings.MEMBERSHIP_LIMIT:
            error_message = "You can currently only be a member of a single organization.  This will hopefully be changed in the future.  Generated for user {0}.".format(self.user)
            log.info(error_message)
            return error_message
        super(Membership, self).save(*args, **kwargs) # Call the "real" save() method.

class UserProfile(models.Model):
    #TODO: Add in a callback where if user identifies as "administrator", then they can create an organization
    #Each userprofile has one user, and vice versa
    user = models.OneToOneField(User, unique=True, blank=True,null=True)
    #TODO: Potentially support users being in multiple orgs, but will be complicated
    #Add in userinfo here.  Location, etc
    name = models.TextField(blank=True,null=True)
    #User role in their organization
    role = models.CharField(max_length=20,blank=True,null=True)
    throttle_at = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        permissions = (
            ("view_userprofile", "Can view userprofile"),
        )

class Course(models.Model):
    #A user can have many courses, and a course can have many users
    users = models.ManyToManyField(User)
    #A course can be shared between organizations
    organizations = models.ManyToManyField(Organization)
    #Each course has a name!
    course_name = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_course", "Can view course"),
        )

class Problem(models.Model):
    #A course has many problems, and a problem can be used in many courses
    courses = models.ManyToManyField(Course)
    #Max scores for one or many targets
    max_target_scores = models.TextField(default=json.dumps([1]))
    #If additional numeric predictors are being sent, the count of them
    number_of_additional_predictors = models.IntegerField(default=0)
    #Prompt of the problem
    prompt = models.TextField(default="")
    #If org has subscriptions to premium feedback models
    premium_feedback_models = models.TextField(default=json.dumps([]))
    name = models.TextField(default="")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_problem", "Can view problem"),
        )

class Essay(models.Model):
    #Each essay is written for a specific problem
    problem = models.ForeignKey(Problem)
    #Each essay is written by a specified user
    user = models.ForeignKey(User, null=True)
    #Each essay is associated with an organization
    organization = models.ForeignKey(Organization, null=True)
    #Each user writes text (their essay)
    essay_text = models.TextField()
    #Schools may wish to send additional predictors (student grade level, etc)
    additional_predictors = models.TextField(default=json.dumps([]))
    #The type of essay (train or test)  see EssayTypes class
    essay_type = models.CharField(max_length=20)
    has_been_ml_graded = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_instructor_scored(self):
        return self.essaygrade_set.filter(grader_type=GraderTypes.instructor).order_by("-modified")[:1]

    class Meta:
        permissions = (
            ("view_essay", "Can view essay"),
        )

class EssayGrade(models.Model):
    #Each essaygrade is for a specific essay
    essay = models.ForeignKey(Essay)
    #How the essay was scored for numerous targets
    target_scores = models.TextField()
    #What type of grader graded it
    grader_type = models.CharField(max_length=20)
    #Feedback from the grader
    feedback = models.TextField()
    #Annotated text from the grader
    annotated_text = models.TextField(default="")
    #Scores on premium feedback model, if any
    premium_feedback_scores = models.TextField(default=json.dumps([]))
    #whether or not the grader succeeded
    success = models.BooleanField()
    #For peer grading and staff grading, we will use this
    user = models.ForeignKey(User,blank=True,null=True)
    #Confidence value from the grader
    confidence = models.DecimalField(max_digits=10,decimal_places=9, default=1)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ("view_essaygrade", "Can view essaygrade"),
        )


#MODEL SIGNAL CALLBACKS

def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a user profile based on a signal from User when it is created
    """
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


def pre_delete_problem(sender, instance, **kwargs):
    """
    Deletes essays associated with a problem when it is deleted
    """
    essays = Essay.objects.filter(problem=instance)
    essays.delete()

def pre_delete_essay(sender, instance, **kwargs):
    """
    Deletes essay grades associated with an essay when it is deleted
    """
    essay_grades = EssayGrade.objects.filter(essay=instance)
    essay_grades.delete()

def pre_delete_essaygrade(sender,instance, **kwargs):
    """
    Ensures that an ML model will be retrained if an old ML scored grade is removed for some reason
    """
    essay = instance.essay
    ml_graded_count = essay.essaygrade_set.filter(grader_type=GraderTypes.machine).count()
    if ml_graded_count<=1:
        essay.has_been_ml_graded=False
        essay.save()

def pre_delete_user(sender,instance,**kwargs):
    """
    Removes the user's profile and removes foreign key relations from objects
    """
    try:
        user_profile = instance.profile
    except SiteProfileNotAvailable:
        log.error("Could not get profile for user {0}".format(instance.username))
        return
    essays = instance.essay_set.all()
    essay_grades = instance.essaygrade_set.all()
    user_profile.delete()
    essays.update(user=None)
    essay_grades.update(user=None)

def add_user_to_groups(sender,instance,**kwargs):
    user = instance.user
    org = instance.organization
    group_name = get_group_name(instance)
    if not Group.objects.filter(name=group_name).exists():
        group = Group.objects.create(name=group_name)
        group.save()
    else:
        group = Group.objects.get(name=group_name)
    user.groups.add(group)
    user.save()

def remove_user_from_groups(sender,instance,**kwargs):
    user = instance.user
    org = instance.organization
    group_name = get_group_name(instance)
    user.groups.filter(name=group_name).delete()
    user.save()

def get_group_name(membership):
    group_name = "{0}_{1}".format(membership.organization.id,membership.role)
    return group_name

def add_creator_permissions(sender, instance, **kwargs):
    try:
        instance_name = instance.__class__.__name__.lower()
        if isinstance(instance, User):
            user = instance
        elif isinstance(instance, UserProfile):
            user=instance.user
        else:
            user = get_request().user
        if instance_name in PERMISSION_MODELS:
            for perm in PERMISSIONS:
                assign_perm('{0}_{1}'.format(perm, instance_name), user, instance)
    except:
        log.debug("Cannot generate perms.  This is probably okay.")

#Django signals called after models are handled
pre_save.connect(remove_user_from_groups, sender=Membership)

post_save.connect(create_user_profile, sender=User)
post_save.connect(create_api_key, sender=User)
post_save.connect(add_user_to_groups, sender=Membership)
post_save.connect(add_creator_permissions)

pre_delete.connect(pre_delete_problem,sender=Problem)
pre_delete.connect(pre_delete_essay,sender=Essay)
pre_delete.connect(pre_delete_essaygrade,sender=EssayGrade)
pre_delete.connect(pre_delete_user, sender=User)
pre_delete.connect(remove_user_from_groups, sender=Membership)

#Maps the get_profile() function of a user to an attribute profile
User.profile = property(lambda u: u.get_profile())

#Register models with the django admin
admin.site.register(Organization)
admin.site.register(Course)
admin.site.register(Problem)
admin.site.register(Essay)
admin.site.register(EssayGrade)
admin.site.register(Membership)










