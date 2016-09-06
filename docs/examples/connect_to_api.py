"""
Example 1: In this example, we will try some basic API connections.
"""

from common_settings import *

#This queries the top level schema and gets all of the available models, and their associated endpoints and schema.
#The ?format=json is needed to let the API know how to return the data.
#Supported formats are 'json', 'jsonp', 'xml', 'yaml', 'plist'.
response = requests.get(API_BASE_URL + "/essay_site/api/v1/?format=json")

#This status code should be 200.  If it is not, verify that you are running the api server at the API_BASE_URL
#You can use python manage.py runserver 127.0.0.1:7999 --nostatic to accomplish this.
print("Status Code: {0}".format(response.status_code))

#Decode the json serialized response into a python object.
rj = response.json()
print(rj)

#Loop through the json object and print out the data.
for model in rj:
    print("Model: {0} Endpoint: {1} Schema: {2}".format(model, rj[model]['list_endpoint'], rj[model]['schema']))

#Now, let's try to get the schema for a single model.
response = requests.get(API_BASE_URL + rj['essay']['schema'] + "?format=json")

#This should get a 401 error if you are not logged in.
print("Status Code: {0}".format(response.status_code))


