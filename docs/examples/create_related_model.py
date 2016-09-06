"""
Example 5: In this example, we will create a course object and relate it to our organization object we created earlier.
"""

from common_settings import *

#This is the same login code that we used previously
login_url = API_BASE_URL + "/essay_site/login/"
data = {
    'username' : 'test',
    'password' : 'test'
}
headers = {'content-type': 'application/json'}
session = requests.session()
response = session.post(login_url, data=json.dumps(data),headers=headers)

#We want to create a course object and relate it to our organization object.
# To do this, let's first find our organization object.
response = session.get(API_BASE_URL + "/essay_site/api/v1/organization/?format=json")

#Now, let's get the text of the response
response_text = json.loads(response.text)

#And then let's get the object that we created in the last example
organization_object = response_text["objects"][0]
organization_resource_uri = organization_object['resource_uri']

#The resource uri is how we identify objects and relate them to each other.
#We can see that the organization object has a resource uri field.
#We can also see that the users, memberships, and courses fields relate the object to other objects via uris.

#Now, let's get the schema for a course.
response = session.get(API_BASE_URL + "/essay_site/api/v1/course/schema/?format=json")
course_schema = json.loads(response.text)

#this will show us what data we need to provide for each field
for field in course_schema['fields'].keys():
    field_data = course_schema['fields'][field]
    print "Name: {0} || Can be blank: {1} || Type: {2} || Help Text: {3}".format(field,field_data['nullable'],field_data['type'],field_data['help_text'])

#The fields id, created, and modified are automatically generated and we do not need to provide them.
#Given this, we only need to provide the non-blank field course_name
#However, since we want to link to our organization, let's also add that in.
course = {'course_name' : 'Test Course', 'organizations' : [organization_resource_uri]}
headers = {'content-type': 'application/json'}

#This will create our new course object using our name and organizations
response = session.post(API_BASE_URL + "/essay_site/api/v1/course/?format=json", data=json.dumps(course), headers=headers)
print "Created object: {0}".format(response.text)

#We can now query the API to find our created course
#We will see that id, created, and modified fields were automatically generated, along with a resource_uri
response = session.get(API_BASE_URL + "/essay_site/api/v1/course/?format=json")
response_text = json.loads(response.text)
course_object = response_text["objects"][0]
print course_object

