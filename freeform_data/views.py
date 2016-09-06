import django.contrib.auth
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
import logging

log=logging.getLogger(__name__)

@csrf_exempt
def login(request):
    """
    Handles external login request.
    """
    if request.method != 'POST':
        return error_response('Must query using HTTP POST.')

    p = dict(request.POST.copy())
    if p == {}:
        p = request.body

    try:
        p = json.loads(p)
    except:
        pass

    if not p.has_key('username') or not p.has_key('password'):
        return error_response('Insufficient login info')
    if isinstance(p['username'], list):
        p['username'] = p['username'][0]

    if isinstance(p['password'], list):
        p['password'] = p['password'][0]
    user = django.contrib.auth.authenticate(username=p['username'], password=p['password'])
    if user is not None:
        django.contrib.auth.login(request, user)
        return success_response('Logged in.')
    else:
        return error_response('Incorrect login credentials.')

def logout(request):
    """
    Uses django auth to handle a logout request
    """
    django.contrib.auth.logout(request)
    return success_response('Goodbye')

def success_response(message):
    return generic_response(message, True)

def error_response(message):
    return generic_response(message, False)

def generic_response(message, success):
    message = {'success' : success, 'message' : message}
    return HttpResponse(json.dumps(message))

def status(request):
    """
    Returns a simple status update
    """
    return success_response("Status: OK")