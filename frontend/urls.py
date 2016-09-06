from django.conf.urls import patterns, url

urlpatterns =patterns('frontend.views',
    url(r'^course/$','course'),
    url(r'^user/$','user'),
    url(r'^problem/$','problem'),
    url(r'^essay/$','essay'),
    url(r'^essaygrade/$','essaygrade'),
    url(r'^membership/$','membership'),
    url(r'^userprofile/$','userprofile'),
    url(r'^organization/$','organization'),
    url(r'^$','index'),
)



