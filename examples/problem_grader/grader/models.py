from django.db import models
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.db.models.signals import post_save, pre_save
import random
import string
from django.conf import settings
import requests
import json
import logging

log= logging.getLogger(__name__)

class Rubric(models.Model):
    """
    The rubric object is a way to locally store data about rubric options.
    Each rubric is associated with a problem object stored on the API side.
    """

    #Each rubric is specific to a problem and a user.
    associated_problem = models.IntegerField()
    user = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def get_scores(self):
        """
        Calculate the final score for a given rubric.
        """
        scores = []
        all_scores = []
        final_score=0
        max_score = 0
        options = self.get_rubric_dict()
        for option in options:
            #Add to all_scores for each of the scores
            all_scores.append(option['option_points'])
            #If the student was marked as correct for a given option, add it to the score
            if option['selected']:
                scores.append(option['option_points'])

        if len(scores)>0:
            final_score = sum(scores)

        if len(all_scores)>0:
            max_score = sum(all_scores)

        return {
            'score' : final_score,
            'max_score' : max_score
        }

    def get_rubric_dict(self):
        """
        Get the rubric in dictionary form.
        """
        options = []
        #Bundle up all of the rubric options
        option_set = self.rubricoption_set.all().order_by('id')
        for option in option_set:
            options.append(model_to_dict(option))
        return options

class RubricOption(models.Model):
    """
    Each rubric has multiple options
    """
    #Associate options with rubrics
    rubric = models.ForeignKey(Rubric)
    #Number of points the rubric option is worth
    option_points = models.IntegerField()
    #Text to show to users for this option
    option_text = models.TextField()
    #Whether or not this option is selected (ie marked correct)
    selected = models.BooleanField(default=False)

class UserProfile(models.Model):
    """
    Every user has a profile.  Used to store additional fields.
    """
    user = models.OneToOneField(User)
    #Api key
    api_key = models.TextField(default="")
    #Api username
    api_user = models.TextField(default="")
    #whether or not an api user has been created
    api_user_created = models.BooleanField(default=False)

    def get_api_auth(self):
        """
        Returns the api authentication dictionary for the given user
        """
        return {
            'username' : self.api_user,
            'api_key' : self.api_key
        }


def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a user profile based on a signal from User when it is created
    """
    #Create a userprofile if the user has just been created, don't if not.
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
    else:
        return

    #If a userprofile was not created (gotten instead), then don't make an api user
    if not created:
        return

    #Create a random password for the api user
    random_pass = ''.join([random.choice(string.digits + string.letters) for i in range(0, 15)])

    #Data we will post to the api to make a user
    data = {
        'username' : instance.username,
        'password' : random_pass,
        'email' : instance.email
        }

    headers = {'content-type': 'application/json'}

    #Now, let's try to get the schema for the create user model.
    create_user_url = settings.FULL_API_START + "createuser/"
    counter = 0
    status_code = 400

    #Try to create the user at the api
    while status_code==400 and counter<2 and not instance.profile.api_user_created:
        try:
            #Post our information to try to create a user
            response = requests.post(create_user_url, data=json.dumps(data),headers=headers)
            status_code = response.status_code
            #If a user has been created, store the api key locally
            if status_code==201:
                instance.profile.api_user_created = True
                response_data = json.loads(response.content)
                instance.profile.api_key = response_data['api_key']
                instance.profile.api_user = data['username']
                instance.profile.save()
        except:
            log.exception("Could not create an API user!")
            instance.profile.save()
        counter+=1
        #If we could not create a user in the first pass through the loop, add to the username to try to make it unique
        data['username'] += random.choice(string.digits + string.letters)

post_save.connect(create_user_profile, sender=User)

#Maps the get_profile() function of a user to an attribute profile
User.profile = property(lambda u: u.get_profile())
