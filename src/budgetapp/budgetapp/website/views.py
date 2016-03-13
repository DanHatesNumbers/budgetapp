from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import PermissionDenied
from . import models, forms

class IndexView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    template_name = 'index.html'

    def __init__(self, *args, **kwargs):
        super(IndexView, self).__init__(*args, **kwargs)
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
        super(OneOffAddView, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None) 

    def form_valid(self, form):
        user = self.request.user
        newtransaction = models.OneOffTransaction()
        newtransaction.amount = form.cleaned_data['amount']
        newtransaction.date = form.cleaned_data['date']
        newtransaction.owner = user
        newtransaction.save()
        return super(OneOffAddView, self).form_valid(form)

class OneOffEditView(LoginRequiredMixin, FormView):
    template_name = 'oneoffedit.html'
    success_url = '/'
    form_class = forms.OneOffTransactionForm

    def get(self, request, *args, **kwargs):
        self.pk = kwargs.pop('pk', None)
        return super(OneOffEditView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.pk = kwargs.pop('pk', None)
        return super(OneOffEditView, self).post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OneOffEditView, self).get_context_data(**kwargs)
        context['pk'] = self.pk
        return context

    def get_form(self, form_class):
        try:
            oneoff = models.OneOffTransaction.objects.get(id=self.pk)
            return form_class(instance=oneoff, **self.get_form_kwargs())
        except models.OneOffTransaction.DoesNotExist:
            raise Http404("Transaction can not be found")

    def form_valid(self, form):
        editedoneoff = form.save(commit=False)
        if models.OneOffTransaction.objects.get(id=self.pk).owner == self.request.user:
            editedoneoff.save()
            return super(OneOffEditView, self).form_valid(form)
        else:
            raise PermissionDenied()

class RecurringAddView(LoginRequiredMixin, FormView):
    template_name = 'recurringadd.html'
    success_url = '/'
    form = forms.RecurringTransactionForm()
    form_class = forms.RecurringTransactionForm

    def __init__(self, *args, **kwargs):
        super(RecurringAddView, self).__init__(*args, **kwargs)
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
