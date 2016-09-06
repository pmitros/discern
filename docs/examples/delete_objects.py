'''
This isn't used in the tutorial directly but you may find it handy to clean up
if the repository gets messy. 
'''

from common_settings import *
from pprint import *

session = requests.session()
response = login_to_discern(session)

#  Exploring the discern APIs?  Want to delete all objects? Here you go.

# problems
problem_response = session.get(API_BASE_URL + "/essay_site/api/v1/problem/?offset=0&limit=200&f?format=json", 
        headers=headers)

for p in json.loads(problem_response.text)['objects']:
	print (u"Problem problem: {0}, URI: {1} ".format(p['prompt'], p['resource_uri']))
	session.delete(API_BASE_URL + p['resource_uri'] + "?format=json")

# problem_response = session.delete(API_BASE_URL + "/essay_site/api/v1/problem/1/?format=json", 
#  	headers=headers)

# courses 
course_response = session.delete(API_BASE_URL + "/essay_site/api/v1/course/1/?format=json", 
 	headers=headers)


# organizations. 
org_response = session.delete(API_BASE_URL + "/essay_site/api/v1/organization/1/?format=json", 
	headers=headers)
