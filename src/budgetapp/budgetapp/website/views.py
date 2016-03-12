from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView 
from django.contrib.auth.models import User
from . import models

class IndexView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    template_name = 'index.html'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

    def get(self, *args, **kwargs): 
        context = {
            'oneoff': self.request.user.oneofftransaction_set.all(),
            'recurring': self.request.user.recurringtransaction_set.all(),
        }
        return render(self.request,'index.html', context)
