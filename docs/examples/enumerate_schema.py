'''
Tutorial - Getting started - the API
Enumates the schema API for course. 
'''

from common_settings import *

session = requests.session()
response = login_to_discern(session)

#Now, let's get the schema for a course.
response = session.get(API_BASE_URL + "/essay_site/api/v1/course/schema/?format=json")
course_schema = json.loads(response.text)

#this will show us what data we need to provide for each field
for field in sorted(course_schema['fields'].keys()):
    field_data = course_schema['fields'][field]
    print "Name: {0} \n\t Can be blank: {1} \n\t Type: {2} \n\t Help Text: {3}\n".format(field,field_data['nullable'],field_data['type'],field_data['help_text'])

