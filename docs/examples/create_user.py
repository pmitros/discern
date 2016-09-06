"""
Example 2: In this example, we will create a user.
"""


from common_settings import *

#In order to create a user, we need to define a username and a password
data = {
    'username' : 'test',
    'password' : 'test',
    'email' : 'test@test.com'
}

#We need to explicitly define the content type to let the API know how to decode the data we are sending.
headers = {'content-type': 'application/json'}

#Now, let's try to get the schema for the create user model.
create_user_url = API_BASE_URL + "/essay_site/api/v1/createuser/"
response = requests.post(create_user_url, data=json.dumps(data),headers=headers)

#This should have a status code of 201, indicating that the user was created correctly.
#If you already have a user with username 'test', you will get a 400 error.
print("Status Code: {0}".format(response.status_code))