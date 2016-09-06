import datetime
from haystack.indexes import SearchIndex, CharField, DateTimeField, BooleanField, DecimalField
from haystack import site
from models import Organization, Course, Problem, Essay, EssayGrade

class BaseIndex(SearchIndex):
    """
    Define a base search index class for all models.  Fields text, created, and modified are generic across all models.
    See haystack documentation for what the text field and document=True mean.  Templates have to be added to
    templates/search/indexes/freeform_data.
    """
    text = CharField(document=True, use_template=True)
    created = DateTimeField(model_attr='created')
    modified = DateTimeField(model_attr='modified')
    model_type = None

    def get_model(self):
        return self.model_type

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_model().objects.all()

class OrganizationIndex(BaseIndex):
    model_type = Organization

class CourseIndex(BaseIndex):
    model_type = Course

class ProblemIndex(BaseIndex):
    model_type = Problem

class EssayIndex(BaseIndex):
    type = CharField(model_attr="essay_type")
    ml_graded = BooleanField(model_attr="has_been_ml_graded")
    model_type = Essay

class EssayGradeIndex(BaseIndex):
    success = BooleanField(model_attr="success")
    confidence = DecimalField(model_attr="confidence")
    model_type = EssayGrade

#Register all of the search indexes.  Must be done in pairs.
site.register(Organization, OrganizationIndex)
site.register(Course, CourseIndex)
site.register(Problem, ProblemIndex)
site.register(Essay, EssayIndex)
site.register(EssayGrade, EssayGradeIndex)