import json
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
import logging
log = logging.getLogger(__name__)

class JSONListValidator(object):
    """
    A validator for json lists that are entered into the API
    """
    message = _('Invalid Json List.')

    def __init__(self, matching_list=None, message=None, matching_list_len = None):
        """
        matching_list - the list to match the input values with.  For example, if we are comparing input target values with max target values from the problem object.
        matching_list_len - Used when we only want to match length.
        message- custom error message if desired.
        """
        self.matching_list = matching_list
        self.matching_list_len = None
        if message is not None:
            self.message = message

        #If we have a matching_list_len, use it
        if matching_list_len is not None and isinstance(matching_list_len, int):
            self.matching_list_len = matching_list_len

        #If we have a matching_list, use it.
        if self.matching_list is not None:
            try:
                self.matching_list = json.loads(self.matching_list)
            except Exception:
                pass

            self.matching_list_len = len(self.matching_list)

    def __call__(self, value):
        """
        Validates that the input is valid json and matches other input criteria
        value - A python list or json encoded list
        """

        #Try to load the json
        try:
            value = json.loads(value)
        except Exception:
            pass

        #Value must be a list!
        if not isinstance(value,list):
            error_message = "You entered a non-list entry for value, or entered bad json. {0}".format(value)
            raise ValidationError(error_message)

        value_len = len(value)

        #Each value must be an integer
        for val in value:
            if not isinstance(val,int):
                error_message="You entered a non-integer value in your score list. {0}".format(value)
                raise ValidationError(error_message)

        #Validate the lengths to ensure they match
        if self.matching_list_len is not None:
            if self.matching_list_len!=value_len:
                error_message = "You entered more target scores than exist in the corresponding maximum list in the problem.  {0} vs {1}".format(value_len, self.matching_list_len)
                raise ValidationError(error_message)

        #Validate each value to make sure it is less than the max allowed.
        if self.matching_list is not None:
            for i in xrange(0,self.matching_list_len):
                if value[i]>self.matching_list[i]:
                    error_message = "Value {i} in provided scores greater than max defined in problem. {value} : {matching}".format(i=i, value=value, matching=self.matching_list)
                    raise ValidationError(error_message)



