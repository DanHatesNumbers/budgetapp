from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import auth

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^transactions/oneoff/add$', views.OneOffAddView.as_view(), name='oneoff_add'),
    url(r'^transactions/oneoff/(?P<pk>\d+)/edit$', views.OneOffEditView.as_view(), name='oneoff_edit'),
    url(r'^transactions/oneoff/(?P<pk>\d+)/delete$', views.OneOffDeleteView.as_view(), name='oneoff_delete'),
    url(r'^transactions/recurring/add$', views.RecurringAddView.as_view(), name='recurring_add'),
    url(r'^transactions/recurring/(?P<pk>\d+)/edit$', views.RecurringEditView.as_view(), name='recurring_edit'),
    url(r'^transactions/recurring/(?P<pk>\d+)/delete$', views.RecurringDeleteView.as_view(), name='recurring_delete'),
    url(r'^balancesheet$', views.BalanceSheetView.as_view(), name='balance_sheet'),
    url(r'^login$', auth.views.login),
    url(r'^logout$', auth.views.logout),
    url(r'^register$', views.UserRegistrationView.as_view(), name='register'),
    url(r'^profile$', views.UserProfileManagementView.as_view(), name='profile'),
]
