from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy
from django.db.models.query_utils import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import DeleteView, UpdateView

import datetime
from decimal import Decimal
import itertools
from operator import attrgetter

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
    form_class = forms.BalanceSheetForm
    success_url = reverse_lazy('balance_sheet')
    template_name = "balancesheet.html"

    def get(self, request, *args, **kwargs):
        balance = request.session.get('balance', Decimal(0.0))
        initial = {'balance': balance}
        form = self.form_class(initial=initial)

        transaction_list = self.generate_transaction_list(balance)
        paginator = Paginator(transaction_list, 25)
        page = self.request.GET.get('page')
        try:
            transactions = paginator.page(page)
        except PageNotAnInteger:
            transactions = paginator.page(1)
        except EmptyPage:
            transactions = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {'form': form, 'transactions': transactions})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            request.session['balance'] = form.cleaned_data['balance']
            return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})

    def generate_transaction_list(self, balance):
        end_date = datetime.datetime.now().replace(year=2017)
        oneoffs = list(self.request.user.oneofftransaction_set.filter(date__gte=datetime.date.today()))

        end_date_optional = Q(end_date__isnull=True)
        end_date_in_range = Q(end_date__gte=datetime.date.today())
        recurrings = self.request.user.recurringtransaction_set.filter(end_date_optional | end_date_in_range)

        expanded_recurrings = list()
        for transaction in recurrings:
            dates = transaction.get_dates(end_date)
            expanded_oneoffs = map(lambda date: models.OneOffTransaction.create(date.date(), transaction.amount, transaction.owner, transaction.name), dates)
            expanded_recurrings += filter(lambda transaction: datetime.date.today() <= transaction.date, expanded_oneoffs)

        all_transactions = sorted(sorted(oneoffs + expanded_recurrings, key=attrgetter('amount')), key=attrgetter('date'))
        current_balance = Decimal(balance)
        for transaction in all_transactions:
            current_balance += transaction.amount
            transaction.balance = current_balance

        return all_transactions

class UserRegistrationView(FormView):
    form_class = forms.UserRegistrationForm
    success_url = '/'
    template_name = 'registration/register.html'

    def form_valid(self, form):
        user = models.User.objects.create_user(form.cleaned_data['email'], form.cleaned_data['password2'])
        authenticated_user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password2'])
        login(self.request, authenticated_user)
        return super(UserRegistrationView, self).form_valid(form)

class UserProfileManagementView(FormView):
    form_class = forms.UserProfileManagementForm
    success_url = reverse_lazy('profile')
    template_name = "registration/profile.html"

    def get(self, request, *args, **kwargs):
        self.user = request.user
        self.request = request
        return super(UserProfileManagementView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.user = request.user
        self.request = request
        return super(UserProfileManagementView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserProfileManagementView, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        if form.cleaned_data['new_password2']:
            self.user.set_password(form.cleaned_data['new_password2'])
            self.user.save()
            update_session_auth_hash(self.request, self.user)

        return super(UserProfileManagementView, self).form_valid(form)
