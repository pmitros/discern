"""
Define some constants and imports that we will use for all the examples.
"""

#Common imports.
#Requests allows us to make http GET/POST/PUT, etc requests.
#See http://docs.python-requests.org/en/latest/ for documentation
import requests
#JSON is a format for transferring data over the web.  This imports a json handling library.
#See http://en.wikipedia.org/wiki/JSON for information on JSON.
import json

from pprint import *

#This tells us where the API is running.
API_BASE_URL = "http://127.0.0.1:7999"

headers = {'content-type': 'application/json'}

# Most of the scripts will need to login, use this function to avoid repeating code. 
def login_to_discern(session, username='test', password='test'):
    login_url = API_BASE_URL + "/essay_site/login/"
    return session.post(
        login_url,
        json.dumps({
        'username': username,
        'password': password, }),
        headers=headers)
