from django.conf.urls import *

urlpatterns=patterns('django.contrib.auth.views',
                     url(r'^login/$','login'),
                     url(r'^logout/$','logout'),
                     )

urlpatterns +=patterns('grader.views',
                       url(r'^register/$','register'),
                       url(r'^$','index'),
                       url(r'^course/$','course'),
                       url(r'^action/$','action'),
                       url(r'^problem/$','problem'),
                       url(r'^write_essays/$','write_essays'),
                       url(r'^grade_essays/$','grade_essays'),
                       )
