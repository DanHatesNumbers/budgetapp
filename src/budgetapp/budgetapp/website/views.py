from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import DeleteView, UpdateView

import datetime
import itertools

from . import forms, models

class IndexView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    redirect_field_name = 'redirect_to'
    template_name = 'index.html'

    def __init__(self, *args, **kwargs):
        super(IndexView, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

    def get(self, *args, **kwargs): 
        end_date_optional = Q(end_date__isnull=True)
        end_date_in_range = Q(end_date__gte=datetime.date.today())
        context = {
            'oneoff': self.request.user.oneofftransaction_set.filter(date__gte=datetime.date.today()),
            'recurring': self.request.user.recurringtransaction_set.filter(end_date_optional | end_date_in_range)
        }
        return render(self.request,'index.html', context)

class OneOffAddView(LoginRequiredMixin, FormView):
    form = forms.OneOffTransactionForm()
    form_class = forms.OneOffTransactionForm
    success_url = '/'
    template_name = 'oneoffadd.html'

    def __init__(self, *args, **kwargs):
        super(OneOffAddView, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None) 

    def form_valid(self, form):
        user = self.request.user
        newtransaction = form.save(commit=False)
        newtransaction.owner = user
        newtransaction.save()
        return super(OneOffAddView, self).form_valid(form)

class OneOffEditView(LoginRequiredMixin, UpdateView):
    form_class = forms.OneOffTransactionForm
    model = models.OneOffTransaction
    success_url = '/'
    template_name = 'oneoffedit.html'

    def get(self, request, *args, **kwargs):
        self.user = request.user
        return super(OneOffEditView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.user = request.user
        return super(OneOffEditView, self).post(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(OneOffEditView, self).get_object(queryset)
        if obj.owner == self.user:
            return obj
        else:
            raise PermissionDenied()

    def form_valid(self, form):
        editedoneoff = form.save(commit=False)
        if self.get_object().owner == self.user:
            editedoneoff.save()
            return super(OneOffEditView, self).form_valid(form)
        else:
            raise PermissionDenied()

class OneOffDeleteView(LoginRequiredMixin, DeleteView):
    model = models.OneOffTransaction
    success_url = '/'
    template_name = 'oneoffdelete.html'
    
    def delete(self, request, *args, **kwargs):
        oneoff = self.get_object()
        if oneoff.owner == request.user:
            oneoff.delete()
            return HttpResponseRedirect(OneOffDeleteView.success_url)
        else:
            raise PermissionDenied()

class RecurringAddView(LoginRequiredMixin, FormView):
    form = forms.RecurringTransactionForm()
    form_class = forms.RecurringTransactionForm
    success_url = '/'
    template_name = 'recurringadd.html'

    def __init__(self, *args, **kwargs):
        super(RecurringAddView, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

    def form_valid(self, form):
        user = self.request.user
        newtransaction = form.save(commit=False)
        newtransaction.owner = user
        newtransaction.save()
        return super(RecurringAddView, self).form_valid(form)

class RecurringEditView(LoginRequiredMixin, UpdateView):
    form_class = forms.RecurringTransactionForm
    model = models.RecurringTransaction
    success_url = '/'
    template_name = 'recurringedit.html'

    def get(self, request, *args, **kwargs):
        self.user = request.user
        return super(RecurringEditView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.user = request.user
        return super(RecurringEditView, self).post(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(RecurringEditView, self).get_object(queryset)
        if obj.owner == self.user:
            return obj
        else:
            raise PermissionDenied()

    def form_valid(self, form):
        editedoneoff = form.save(commit=False)
        if self.get_object().owner == self.user:
            editedoneoff.save()
            return super(RecurringEditView, self).form_valid(form)
        else:
            raise PermissionDenied()

class RecurringDeleteView(LoginRequiredMixin, DeleteView):
    model = models.RecurringTransaction
    success_url = '/'
    template_name = 'recurringdelete.html'
    
    def delete(self, request, *args, **kwargs):
        oneoff = self.get_object()
        if oneoff.owner == request.user:
            oneoff.delete()
            return HttpResponseRedirect(RecurringDeleteView.success_url)
        else:
            raise PermissionDenied()

class BalanceSheetView(LoginRequiredMixin, TemplateView):
    template_name = "balancesheet.html"

    def __init__(self, *args, **kwargs):
        super(BalanceSheetView, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

    def get(self, *args, **kwargs):
        end_date = datetime.datetime.now().replace(year=2017)
        oneoffs = list(self.request.user.oneofftransaction_set.filter(date__gte=datetime.date.today()))

        end_date_optional = Q(end_date__isnull=True)
        end_date_in_range = Q(end_date__gte=datetime.date.today())
        recurrings = self.request.user.recurringtransaction_set.filter(end_date_optional | end_date_in_range)

        expanded_recurrings = list()
        for transaction in recurrings:
            dates = transaction.get_dates(end_date)
            expanded_oneoffs = map(lambda date: models.OneOffTransaction.create(date.date(), transaction.amount, transaction.owner, transaction.name), dates)
            expanded_recurrings += expanded_oneoffs

        all_transactions = sorted(oneoffs + expanded_recurrings, key=lambda x: x.date)
        
        context = {"transactions": all_transactions}
        return render(self.request, BalanceSheetView.template_name, context)

