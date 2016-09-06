from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import logging
log = logging.getLogger(__name__)

def index(request):
    return render_to_response("index.html",RequestContext(request))

def userprofile(request):
    return render_to_response("models/userprofile.html", RequestContext(request))

def course(request):
    return render_to_response("models/course.html", RequestContext(request))

def problem(request):
    return render_to_response("models/problem.html", RequestContext(request))

def organization(request):
    return render_to_response("models/organization.html", RequestContext(request))

def essay(request):
    return render_to_response("models/essay.html", RequestContext(request))

def essaygrade(request):
    return render_to_response("models/essaygrade.html", RequestContext(request))

def user(request):
    return render_to_response("models/user.html", RequestContext(request))

def membership(request):
    return render_to_response("models/membership.html", RequestContext(request))