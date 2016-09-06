'''
This is not used in the tutorial but you might find it handy to examine the
status of the Discern Server. 
'''

from common_settings import *
from pprint import *

session = requests.session()
response = login_to_discern(session)

#  enumerate first 20 objects.

problem_response = session.get(API_BASE_URL + "/essay_site/api/v1/problem/?offset=0&limit=20&f?format=json", 
 	headers=headers)

for p in json.loads(problem_response.text)['objects']:
	print (u"Problem problem: {0}, URI: {1} ".format(p['prompt'], p['resource_uri']))

course_response = session.get(API_BASE_URL + "/essay_site/api/v1/course/?offset=0&limit=20&f?format=json", 
 	headers=headers)

for c in json.loads(course_response.text)['objects']:
	print (u"Course name: {0}, URI: {1} ".format(c['course_name'], c['resource_uri']))

org_response = session.get(API_BASE_URL + "/essay_site/api/v1/organization/?offset=0&limit=20&f?format=json", 
 	headers=headers)

for org in json.loads(org_response.text)['objects']:
	print (u"Organization name: {0}, URI: {1} ".format(org['organization_name'], org['resource_uri']))

