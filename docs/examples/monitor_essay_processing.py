'''
Tutorial - This script inspects ease's progress grading essays. 
The assumption is that the populate_essays.py script has been run.
'''

from common_settings import *

# boilerplate login code
session = requests.session()
response = login_to_discern(session)

# Given a resource_uri for an essaygrade, pretty print the values.
def enumerate_grades(essaygrades_uri):
	response = session.get(API_BASE_URL + essaygrades_uri + "?format=json")
	grade = json.loads(response.text)
	print("\t confidence: {0}, score: {1}, type: {2} ".format(grade['confidence'], grade['target_scores'], grade['grader_type']))
	return None
	
response = session.get(API_BASE_URL + "/essay_site/api/v1/essay/?format=json")
essays  = json.loads(response.text)
for e in essays['objects']:
	print ("Scores for essay {0}, problem {1}".format(e['resource_uri'], e['problem']))
	for uri in e['essaygrades']:
		enumerate_grades(uri)
