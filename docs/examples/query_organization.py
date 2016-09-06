"""
Example 4: In this example, we will query our models after logging in and create our own model object.
"""

from common_settings import *

login_url = API_BASE_URL + "/essay_site/login/"

#These are the credentials that we created in the previous example.
data = {
    'username' : 'test',
    'password' : 'test'
}

#We need to explicitly define the content type to let the API know how to decode the data we are sending.
headers = {'content-type': 'application/json'}

#A session allows us to store cookies and other persistent information.
#In this case, it lets the server keep us logged in and make requests as a logged in user.
session = requests.session()
response = session.post(login_url, data=json.dumps(data),headers=headers)
print("Status Code: {0}".format(response.status_code))

#Now, let's try to get all the organization models that we have access to.
response = session.get(API_BASE_URL + "/essay_site/api/v1/organization/?format=json")

#This should get a 401 error if you are not logged in, and a 200 if you are.
print("Status Code: {0}".format(response.status_code))

#At this point, we will get a response from the server that lists all of the organization objects that we have created.
print("Response from server: {0}".format(response.text))

#We have yet to create any organization objects, so we will need to add some in before they can be properly displayed back to us.
#First, let's see what fields the organization model will accept.
response = session.get(API_BASE_URL + "/essay_site/api/v1/organization/schema/?format=json")
#At this point, we will get a response from the server that lists details of how to interact with the organization model
print("Response from server: {0}".format(response.text))

#We should see something like this.  It tells us that we can get, post, put, delete, or patch to organization.  It also tells us the fields that the organization model has.
"""
u'{"allowed_detail_http_methods": ["get", "post", "put", "delete", "patch"], "allowed_list_http_methods": ["get", "post", "put", "delete", "patch"], "default_format": "application/json", "default_limit": 20, "fields": {"courses": {"blank": false, "default": "No default provided.", "help_text": "Many related resources. Can be either a list of URIs or list of individually nested resource data.", "nullable": true, "readonly": false, "related_type": "to_many", "type": "related", "unique": false}, "created": {"blank": true, "default": true, "help_text": "A date & time as a string. Ex: \\"2010-11-10T03:07:43\\"", "nullable": false, "readonly": false, "type": "datetime", "unique": false}, "essays": {"blank": false, "default": "No default provided.", "help_text": "Many related resources. Can be either a list of URIs or list of individually nested resource data.", "nullable": true, "readonly": false, "related_type": "to_many", "type": "related", "unique": false}, "id": {"blank": true, "default": "", "help_text": "Integer data. Ex: 2673", "nullable": false, "readonly": false, "type": "integer", "unique": true}, "memberships": {"blank": false, "default": "No default provided.", "help_text": "Many related resources. Can be either a list of URIs or list of individually nested resource data.", "nullable": true, "readonly": false, "related_type": "to_many", "type": "related", "unique": false}, "modified": {"blank": true, "default": true, "help_text": "A date & time as a string. Ex: \\"2010-11-10T03:07:43\\"", "nullable": false, "readonly": false, "type": "datetime", "unique": false}, "organization_name": {"blank": false, "default": "", "help_text": "Unicode string data. Ex: \\"Hello World\\"", "nullable": false, "readonly": false, "type": "string", "unique": false}, "organization_size": {"blank": false, "default": 0, "help_text": "Integer data. Ex: 2673", "nullable": false, "readonly": false, "type": "integer", "unique": false}, "premium_service_subscriptions": {"blank": false, "default": "[]", "help_text": "Unicode string data. Ex: \\"Hello World\\"", "nullable": false, "readonly": false, "type": "string", "unique": false}, "resource_uri": {"blank": false, "default": "No default provided.", "help_text": "Unicode string data. Ex: \\"Hello World\\"", "nullable": false, "readonly": true, "type": "string", "unique": false}, "users": {"blank": false, "default": "No default provided.", "help_text": "Many related resources. Can be either a list of URIs or list of individually nested resource data.", "nullable": true, "readonly": false, "related_type": "to_many", "type": "related", "unique": false}}}'
"""

#Let's filter this a bit so that we only see available field and their type
#First, the response is a json-encoded string, so let's convert it to a python object
response_json = json.loads(response.text)

#This will display a list of fields and their type
#The related type joins models together.  A url to a specific model will need to be passed to this field (we will
#walk through this later).  For now, let's focus on the string fields.
for field in response_json['fields']:
    print("{0} : {1}".format(field, response_json['fields'][field]['type']))

#This is the data that will be used to construct our organization
data = {
    'organization_name' : "Test",
    'organization_size' : 1,
}

#Let's create our object by posting to the server!
response = session.post(API_BASE_URL + "/essay_site/api/v1/organization/?format=json", data=json.dumps(data), headers=headers)

#We can now see our created object, which has been returned from the server
print "Created object: {0}".format(response.text)

#As before, we can load all responses from the API using json
json_object = json.loads(response.text)

#We can see that some fields were automatically created.  The created and modified fields tell us when the model was made and created.
#Some related fields were also automatically populated.  These will be explained better when related fields are explained.



