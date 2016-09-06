'''
Tutorial - Getting started - create a organization course objects
Here we create an institution(i.e., Reddit). Make a note of the resulting URIs.
We will use them with other example programs. 
'''

from common_settings import *

session = requests.session()
response = login_to_discern(session)

# create an organization
org_response = session.post(API_BASE_URL + "/essay_site/api/v1/organization/?format=json",
                            data=json.dumps({"organization_name": "Reddit"}),
                            headers=headers)

# get the URI for the organization 
#    Let's get the text of the response
organization_object = json.loads(org_response.text)
organization_resource_uri = organization_object['resource_uri']


# create a course and associate it with the organization
course_response = session.post(API_BASE_URL + "/essay_site/api/v1/course/?format=json",
                               data=json.dumps(
                                   {"course_name": "Discern Tutorial",
                                    "organizations": [organization_resource_uri]
                                   }),
                               headers=headers)

# Get the URI for the course
course_object = json.loads(course_response.text)

if course_response.status_code >= 400:
    pprint("status: {0} msg: {1}".format(
        course_response.status_code,
        course_response._content))
    pprint(vars(course_response.request))
    exit(1)

course_uri = course_object['resource_uri']

print ("We will be uses the URI for these objects in other scripts. Please make a note")
print ("org URI: {0} ".format(organization_resource_uri))
print ("course URI: {0} ".format(course_uri))
