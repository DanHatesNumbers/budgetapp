from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from django.contrib.auth.models import User
from . import models, forms

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

class OneOffAddView(LoginRequiredMixin, FormView):
    template_name = 'oneoffadd.html'
    success_url = '/'
    form = forms.OneOffTransactionForm()
    form_class = forms.OneOffTransactionForm

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) 

    def form_valid(self, form):
        user = self.request.user
        newtransaction = models.OneOffTransaction()
        newtransaction.amount = form.cleaned_data['amount']
        newtransaction.date = form.cleaned_data['date']
        newtransaction.owner = user
        newtransaction.save()
        return super(OneOffAddView, self).form_valid(form)

class RecurringAddView(LoginRequiredMixin, FormView):
    template_name = 'recurringadd.html'
    success_url = '/'
    form = forms.RecurringTransactionForm()
    form_class = forms.RecurringTransactionForm

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

    def form_valid(self, form):
        user = self.request.user
        newtransaction = models.RecurringTransaction()
        newtransaction.amount = form.cleaned_data['amount']
        newtransaction.start_date = form.cleaned_data['start_date']
        newtransaction.end_date = form.cleaned_data['end_date']
        newtransaction.base_period = form.cleaned_data['base_period']
        newtransaction.frequency = form.cleaned_data['frequency']
        newtransaction.owner = user
        newtransaction.save()
        return super(RecurringAddView, self).form_valid(form)
