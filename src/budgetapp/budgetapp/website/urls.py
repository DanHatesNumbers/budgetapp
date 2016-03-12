from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.models import User

from . import views

urlpatterns = patterns(
    '', 
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^logout$', 'django.contrib.auth.views.logout'),
)
