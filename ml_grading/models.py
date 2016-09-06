from django.db import models
from django.utils import timezone
import json

CHARFIELD_LEN_SMALL=128
CHARFIELD_LEN_LONG = 1024

class CreatedModel(models.Model):
    #When it was created/modified
    modified=models.DateTimeField(auto_now=True)
    created=models.DateTimeField(auto_now_add=True)

    #Properties of the problem the model was created with
    max_score=models.IntegerField()
    prompt=models.TextField()
    problem = models.ForeignKey("freeform_data.Problem")
    target_number = models.IntegerField(default=0)

    #Properties of the model file
    model_relative_path=models.CharField(max_length=CHARFIELD_LEN_LONG)
    model_full_path=models.CharField(max_length=CHARFIELD_LEN_LONG)

    #Properties of the model itself
    number_of_essays=models.IntegerField()

    #CV is cross-validation, which is a statistical technique that ensures that
    #the models are trained on one part of the data and predicted on another.
    #so the kappa and error measurements are not biased by the data that was used to create the models
    #being used to also evaluate them. (ie, this is "True" error)
    #Kappa is interrater agreement-closer to 1 is better.
    #If the actual scores and the predicted scores perfectly agree, kappa will be 1.
    cv_kappa=models.DecimalField(max_digits=10,decimal_places=9, default=1)

    #Mean absolute error is mean(abs(actual_score-predicted_score))
    #A mean absolute error of .5 means that, on average, the predicted score is +/- .5 points from the actual score
    cv_mean_absolute_error=models.DecimalField(max_digits=15,decimal_places=10, default=1)

    creation_succeeded=models.BooleanField(default=False)
    creation_started =models.BooleanField(default=False)

    #Amazon S3 stuff if we do use it
    model_stored_in_s3=models.BooleanField(default=False)
    s3_public_url=models.TextField(default="")
    s3_bucketname=models.TextField(default="")

    def get_submission_ids_used(self):
        """
        Returns a list of submission ids of essays used to create the model.
        Output:
            Boolean success, list of ids/error message as appropriate
        """

        try:
            submission_id_list=json.loads(self.submission_ids_used)
        except:
            return False, "No essays used or not in json format."

        return True, submission_id_list