from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^essay_site/', include('freeform_data.urls')),
    url(r'^frontend/', include('frontend.urls')),
    url(r'^$', include('frontend.urls')),
    url(r'^accounts/', include('allauth.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^status/', 'freeform_data.views.status')
)

if settings.DEBUG:
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
    urlpatterns+= patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
            'show_indexes' : True,
            }),
        )
