from models import Rubric, RubricOption
import logging

log = logging.getLogger(__name__)

def get_rubric_data(problem_id, target_scores = None):
    """
    Retrieve the local rubric that is associated with a given api problem
    problem_id - the id of the problem object that the rubric is associated with
    target_scores - if we have recieved scores for the problem, pass them in
    """
    #Retrieve the local rubric object
    rubric = Rubric.objects.filter(associated_problem=int(problem_id))
    rubric_dict = []
    if rubric.count()>=1:
        rubric = rubric[0]
        #Get the dictionary representation of the rubric
        rubric_dict = rubric.get_rubric_dict()
    if target_scores is not None:
        #If we have recieved target scores, mark the given rubric options as selected (score of 1 means select, 0 means not selected)
        for i in xrange(0,len(rubric_dict)):
            if target_scores[i]==1:
                rubric_dict[i]['selected'] = True
    return rubric_dict

def create_rubric_objects(rubric_data, request):
    """
    For a given user and problem id, create a local rubric object
    rubric_data - the dictionary data associated with the rubric
    request - the request that the user has made
    """
    #Create the rubric
    rubric = Rubric(associated_problem = int(rubric_data['problem_id']), user = request.user)
    rubric.save()
    #Create each rubric option
    for option in rubric_data['options']:
        option = RubricOption(rubric=rubric, option_points =option['points'], option_text = option['text'])
        option.save()

def delete_rubric_data(problem_id):
    """
    When a problem is deleted, delete its local rubric object
    problem_id - int or string problem id
    """
    Rubric.objects.filter(associated_problem=int(problem_id)).delete()
