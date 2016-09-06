import slumber
import logging
import requests
import json
import os

log = logging.getLogger(__name__)

def join_without_slash(path1, path2):
    """
    Join two paths and ensure that only one slash is used at the join point
    path1 - string path(ie '/base/')
    path2 -string path (ie '/home/')
    """
    if path1.endswith("/"):
        path1 = path1[0:-1]
    if not path2.startswith("/"):
        path2 = "/" + path2

    return path1 + path2

class InvalidValueException(Exception):
    """
    Exception for an invalid value
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SlumberModel(object):
    """
    Wraps an API model, and provides abstractions for get/post/update/delete.  Used to simplify talking with the api.
    See https://github.com/KayEss/django-slumber for more details on slumber.
    """
    #These are not required fields, so don't advertise them as such
    excluded_fields = ['created', 'id', 'resource_uri', 'id', 'modified']
    def __init__(self,api_url, model_type, api_auth):
        """
        api_url - the base url for the api (settings.FULL_API_START)
        model_type - the type of model to encapsulate (ie 'organization')
        api_auth - the api auth dict for a given user (see UserProfile.get_api_auth)
        """
        self.api = slumber.API(api_url)
        self.api_url = api_url
        self.model_type = model_type
        self.api_auth = api_auth
        self.objects=[]

    def get_base_model(self, id = None):
        """
        Gets the start of the slumber model path for an api resource
        """
        #In slumber, the base slumber.API has attributes for each model at the endpoint
        ref = getattr(self.api,self.model_type)
        if id is not None:
            #If we are referencing a specific model id, add it into the base
            ref = ref(id)
        return ref

    def get(self, id = None, data = None, **kwargs):
        """
        Get an object or list of objects from the api
        id - int
        data - Not used
        """
        #Create the arguments to send to the api
        new_arguments = self.api_auth.copy()
        #limit=0 disables pagination
        new_arguments['limit'] = 0

        if id is not None:
            #Get a single object
            self.objects = self.get_base_model(id).get(**new_arguments)
            return self.objects
        else:
            #Get a list of objects
            return self.get_base_model().get(**new_arguments).get('objects', None)

    @property
    def schema(self):
        """
        The schema for the model.
        """
        schema = self.get_base_model().schema.get(**self.api_auth).get('fields', None)
        return schema

    @property
    def required_fields(self):
        """
        Required fields for the model.  These are needed to post to the api.
        """
        schema = self.schema
        required_fields = []
        for field in schema:
            if (not schema[field]['nullable'] or schema[field]['blank']) and field not in self.excluded_fields:
                required_fields.append(field)
        return required_fields

    def post(self, id = None, data = None, **kwargs):
        """
        Posts a new instance to the api
        id - Not used
        data - the data to post
        """
        #Check to see if all required fields are being filled in
        for field in self.required_fields:
            if field not in data:
               error_message = "Key {0} not present in post data, but is required.".format(field)
               log.info(error_message)
               raise InvalidValueException(error_message)
        #Add in the data to post
        new_arguments = self.api_auth.copy()
        new_arguments['data'] = data

        new = self.get_base_model().post(**new_arguments)
        #Add the object to the internal objects dict
        self.objects.append(new)
        return new

    def find_model_by_id(self,id):
        """
        Find a model given its id
        id - int
        """
        match = None
        for i in xrange(0,len(self.objects)):
            loop_obj = self.objects[i]
            if int(loop_obj['id']) == id:
                match = i
                break
        return match

    def delete(self,id = None, data = None, **kwargs):
        """
        Delete a given instance of a model
        id - int, instance to delete
        data - not used
        """
        #Delete the instance
        response = self.get_base_model(id=id).delete(**self.api_auth)

        #Find a match and remove the model from the internal list
        match = self.find_model_by_id(id)
        if match is not None:
            self.objects.pop(match)
        return response

    def update(self, id = None, data = None, **kwargs):
        """
        Update a given instance of a model
        id - int, instance to update
        data - data to update with
        """
        #Refresh the internal model list
        self.get()
        #Add the data to be posted
        new_arguments = self.api_auth.copy()
        new_arguments['data'] = data
        #Update
        response = self.get_base_model(id=id).update(**new_arguments)
        #Update in internal list
        match = self.find_model_by_id(id)
        self.objects[match] = response
        return response

    def action(self, action, id=None, data = None):
        """
        Perform a given action
        action - see the keys in action_dict for the values this can take
        id - integer id if needed for the action
        data - dict data if needed for the action
        """

        #Define the actions that are possible, and map them to functions
        action_dict = {
            'get' : self.get,
            'post' : self.post,
            'update' : self.update,
            'delete' : self.delete,
        }
        #Check to see if action is possible
        if action not in action_dict:
            error = "Could not find action {0} in registered actions.".format(action)
            log.info(error)
            raise InvalidValueException(error)

        #Check to see if id is provided for update and delete
        if action in ['update', 'delete'] and id is None:
            error = "Need to provide an id along with action {0}.".format(action)
            log.info(error)
            raise InvalidValueException(error)

        #check to see if data is provided for update and post
        if action in ['update', 'post'] and data is None:
            error = "Need to provide data along with action {0}.".format(action)
            log.info(error)
            raise InvalidValueException(error)

        #Perform the action
        result = action_dict[action](data=data, id=id)
        return result

class SlumberModelDiscovery(object):
    """
    A class the auto-discovers slumber models by checking the api
    """
    def __init__(self,api_url, api_auth):
        """
        api_url - the base url for the api.  See settings.FULL_API_START.
        api_auth - api auth dict.  See UserProfile.get_api_auth
        """
        self.api_url = api_url
        self.api_auth = api_auth
        #Append format=json to avoid error
        self.schema_url = join_without_slash(self.api_url, "?format=json")

    def get_schema(self):
        """
        Get and load the api schema
        """
        schema = requests.get(self.schema_url, params=self.api_auth)
        return json.loads(schema.content)

    def generate_models(self, model_names = None):
        """
        Using the schema, generate slumber models for each of the api models
        model_names - optional list of slumber models to generate
        """
        schema = self.get_schema()
        slumber_models = {}
        for field in schema:
            if model_names is not None and field not in model_names:
                continue
            field_model = SlumberModel(self.api_url, field, self.api_auth)
            slumber_models[field] = field_model
        return slumber_models



