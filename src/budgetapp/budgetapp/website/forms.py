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

class UserProfileManagementForm(forms.Form):
    current_password = forms.CharField(label='Current Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileManagementForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(UserProfileManagementForm, self).clean()
        new_password1 = cleaned_data['new_password1']
        new_password2 = cleaned_data['new_password2']
        current_password = cleaned_data['current_password']
        if new_password1 and new_password2 and not current_password:
            raise forms.ValidationError("You must provide your current password when changing your password")
        if new_password1 != new_password2:
            raise forms.ValidationError("Your new passwords must match")
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password is incorrect")

        return cleaned_data

