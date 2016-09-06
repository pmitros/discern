'''
Tutorial - Getting started - create a organization, course and problem objects
Here we create an institution(i.e., Reddit). 
'''

from common_settings import *
import praw # Python Reddit API Wrapper

# boilerplate login code
session = requests.session()
response = login_to_discern(session)

# add a problem statement. For the reddit example, we will use the title. 
def add_problem(the_prompt, the_class):
    problem_response = session.post(API_BASE_URL + "/essay_site/api/v1/problem/?format=json",
                                    data=json.dumps({"name": "movie question", "courses": [the_class],
                                                     "prompt": the_prompt, "max_target_scores": json.dumps([10000])}),
                                    headers=headers)
    if problem_response.status_code >= 400:
        print ("Problem creation failure.")
        print("status: {0} msg: {1}".format(
            problem_response.status_code,
            problem_response._content))
        print(vars(problem_response.request))
    problem_object = json.loads(problem_response.text)
    return problem_object['resource_uri']

# Add essay grade objects that are instructor scored and associate each one with an essay.
def add_score(the_essay_uri, the_score):
    score_response = session.post(API_BASE_URL + "/essay_site/api/v1/essaygrade/?format=json",
                                  data=json.dumps({
                                  "essay": the_essay_uri,
                                  "grader_type": "IN",
                                  "success": "true",
                                  "target_scores": json.dumps([the_score])
                                  }),
                                  headers=headers)

    if score_response.status_code >= 400:
        print ("Score creation failure.")
        print("status: {0} msg: {1}".format(
            score_response.status_code,
            score_response._content))
        print(vars(score_response.request))
    # GradeEssay doesn't have a resource_uri field
    return None

# Add an essay objects and associate them with the problem.
# returns resource_uri for the new essay object. 
def add_essay(the_text, the_problem_uri):
    essay_response = session.post(API_BASE_URL + "/essay_site/api/v1/essay/?format=json",
                                  data=json.dumps({
                                  "essay_type": "train",
                                  "essay_text": the_text,
                                  "problem": the_problem_uri,
                                  }), headers=headers)
    if essay_response.status_code >= 400:
        print ("essay creation failure.")
        print("status: {0} msg: {1}".format(
            essay_response.status_code,
            essay_response._content))
        print(vars(essay_response.request))
    essay_object = json.loads(essay_response.text)
    return essay_object['resource_uri']

# use the movie title as problem statement. 
r = praw.Reddit(user_agent='Discern Tutorial')
# get a movie from Reddit
submissions = r.get_subreddit('movies').get_hot(limit=1)
movie = submissions.next()

# TODO: update these two varibles with your results from running create_objects_for_tutorial.py
org_uri = '/essay_site/api/v1/organization/6/'
course_uri = '/essay_site/api/v1/course/28/'

problem_uri = add_problem(movie.title, course_uri)

comment_count = 0
for comment in movie.comments:
    if comment_count > 10:
        break
    essay_uri = add_essay(comment.body, problem_uri)
    add_score(essay_uri, comment.ups - comment.downs)
    comment_count += 1
