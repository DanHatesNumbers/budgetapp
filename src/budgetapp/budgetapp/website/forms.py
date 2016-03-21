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

class BalanceSheetForm(forms.Form):
    balance = forms.DecimalField(max_digits=10, decimal_places=2)

class UserRegistrationForm(forms.Form):
    email = forms.EmailField(label='Email Address')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(UserRegistrationForm, self).clean()
        password1 = cleaned_data['password1']
        password2 = cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError("Passwords did not match")
        if models.User.objects.filter(email=cleaned_data['email']).exists():
            raise forms.ValidationError("Email address already exists")

        return cleaned_data
