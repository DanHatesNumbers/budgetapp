from django import forms
from . import models

class OneOffTransactionForm(forms.ModelForm):

    class Meta:
        model = models.OneOffTransaction
        fields = ('name', 'amount', 'date',)

class RecurringTransactionForm(forms.ModelForm):

    class Meta:
        model = models.RecurringTransaction
        fields = ('name', 'amount', 'start_date', 'end_date', 'base_period', 'frequency',)
