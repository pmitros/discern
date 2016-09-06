def grade(grader_data,student_response):
    result_dict = {'errors': [],'tests': [],'score': 0, 'feedback' : "", 'success' : False, 'confidence' : 1}
    return result_dict

def create(essay_text, scores, prompt):
    result_dict = {'errors': [],'success' : False, 'cv_kappa' : 0, 'cv_mean_absolute_error': 0,
     'feature_ext' : "", 'classifier' : "", 'algorithm' : "C",
     'score' : scores, 'text' : essay_text, 'prompt' : prompt, 's3_public_url' : 'blah'}
    return result_dict