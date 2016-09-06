"""
Example 3: In this example, we will login with our created user.
"""

from common_settings import *

#We can use api key authentication or django session authentication.  In this case, we will login with the django session.

login_url = API_BASE_URL + "/essay_site/login/"

#These are the credentials that we created in the previous example.
data = {
    'username' : 'test',
    'password' : 'test'
}

#We need to explicitly define the content type to let the API know how to decode the data we are sending.
headers = {'content-type': 'application/json'}

#Now, let's try to login with our credentials.
response = requests.post(login_url, json.dumps(data),headers=headers)

# If the user with username test and password test has been created, this should return a 200 code.
print("Status Code: {0}".format(response.status_code))
#This should show us a json dictionary with "message" : "Logged in."
print("Response from server: {0}".format(response.text))