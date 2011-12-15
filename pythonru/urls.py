from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^dashboard/', include(admin.site.urls)),

    url(r'^profiles/', include('scipio.urls')),
    url(r'^forum/',    include('cicero.urls')),
)
