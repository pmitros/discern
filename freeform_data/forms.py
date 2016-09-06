from django import forms
import fields
import django_validators
import logging
from django.forms.fields import Field, FileField, IntegerField, CharField, ChoiceField, BooleanField, DecimalField, EmailField
from django.core.exceptions import ValidationError
from models import ESSAY_TYPES, GRADER_TYPES

log = logging.getLogger(__name__)

class ProblemForm(forms.Form):
    """
    A form to validate Problem resources
    """
    number_of_additional_predictors = IntegerField(min_value=0, required=False)
    prompt = CharField(min_length=0, required=True)
    name = CharField(min_length=0, required=False)
    def __init__(self, problem_object= None, **kwargs):
        super(ProblemForm, self).__init__(**kwargs)
        validator = django_validators.JSONListValidator()
        self.fields['max_target_scores'] = fields.JSONListField(required=True, validators=[validator])

class EssayForm(forms.Form):
    """
    A form to validate Essay resources
    """
    essay_text = CharField(min_length=0, required=True)
    essay_type = ChoiceField(choices=ESSAY_TYPES, required=True)
    def __init__(self, problem_object=None, **kwargs):
        super(EssayForm, self).__init__(**kwargs)
        if problem_object is not None:
            self.add_pred_length = problem_object.get('number_of_additional_predictors',0)
        else:
            self.add_pred_length = 0

        validator = django_validators.JSONListValidator(matching_list_len=self.add_pred_length)

        self.fields['additional_predictors'] = fields.JSONListField(required = False, validators=[validator])

class EssayGradeForm(forms.Form):
    """
    A form to validate essaygrade resources
    """
    grader_type = ChoiceField(choices=GRADER_TYPES, required=True)
    feedback = CharField(min_length=0, required=False)
    annotated_text = CharField(min_length=0, required=False)
    success = BooleanField(required=True)
    confidence = DecimalField(required=False, max_value=1, max_digits=10)
    def __init__(self, problem_object = None, **kwargs):
        super(EssayGradeForm, self).__init__(**kwargs)
        self.max_target_scores = None
        if problem_object is not None:
            self.max_target_scores = problem_object.get('max_target_scores',None)

        validator = django_validators.JSONListValidator(matching_list=self.max_target_scores)

        self.fields['target_scores'] = fields.JSONListField(required = True, validators=[validator])

class UserForm(forms.Form):
    """
    A form to validate User resources
    """
    username = CharField(min_length=3, required=True)
    email = EmailField(min_length=3, required=True)
    password = CharField(widget=forms.PasswordInput())
    def __init__(self, user_object= None, **kwargs):
        super(UserForm, self).__init__(**kwargs)