from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
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
        newtransaction = form.save(commit=False)
        newtransaction.owner = user
        newtransaction.save()
        return super(OneOffAddView, self).form_valid(form)

class OneOffEditView(LoginRequiredMixin, UpdateView):
    template_name = 'oneoffedit.html'
    success_url = '/'
    form_class = forms.OneOffTransactionForm
    model = models.OneOffTransaction

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
    template_name = 'recurringadd.html'
    success_url = '/'
    form = forms.RecurringTransactionForm()
    form_class = forms.RecurringTransactionForm

    def __init__(self, *args, **kwargs):
        super(RecurringAddView, self).__init__(*args, **kwargs)
        self.request = kwargs.pop('request', None)

    def form_valid(self, form):
        user = self.request.user
        newtransaction = form.save(commit=False)
        newtransaction.owner = user
        newtransaction.save()
        return super(RecurringAddView, self).form_valid(form)

class RecurringEditView(LoginRequiredMixin, FormView):
    template_name = 'recurringedit.html'
    success_url = '/'
    form_class = forms.RecurringTransactionForm

    def get(self, request, *args, **kwargs):
        self.pk = kwargs.pop('pk', None)
        return super(RecurringEditView, self).get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.pk = kwargs.pop('pk', None)
        return super(RecurringEditView, self).post(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RecurringEditView, self).get_context_data(**kwargs)
        context['pk'] = self.pk
        return context

    def get_form(self, form_class):
        try:
            oneoff = models.RecurringTransaction.objects.get(id=self.pk)
            return form_class(instance=oneoff, **self.get_form_kwargs())
        except models.RecurringTransaction.DoesNotExist:
            raise Http404("Transaction can not be found")

    def form_valid(self, form):
        editedoneoff = form.save(commit=False)
        if models.RecurringTransaction.objects.get(id=self.pk).owner == self.request.user:
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
