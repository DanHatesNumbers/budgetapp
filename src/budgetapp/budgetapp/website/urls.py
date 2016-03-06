from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = patterns(
    '', 
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^logout$', 'django.contrib.auth.views.logout'),
)
