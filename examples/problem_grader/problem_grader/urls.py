from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grader/', include('grader.urls')),
                       url(r'^$', include('grader.urls')),
                       )

if settings.DEBUG:
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
    urlpatterns+= patterns('',
                           url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.STATIC_ROOT,
                               'show_indexes' : True,
                               }),
                           )
