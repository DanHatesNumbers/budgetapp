from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from datetime import date
from dateutil import relativedelta, rrule
import inflect

from budgetapp.website.UserManager import *

class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

class Transaction(models.Model):
    name = models.CharField(max_length=120, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text='Use positive numbers for credits and negative numbers for debits')
    owner = models.ForeignKey(User)
    is_salary = models.BooleanField(default=False)

    class Meta:
        abstract = True

class OneOffTransaction(Transaction):
    date = models.DateField(help_text='Use dd/mm/yyyy format')

    @classmethod
    def create(cls, transaction_date, amount, owner, is_salary, name = None):
        transaction = cls()
        transaction.date = transaction_date
        transaction.amount = amount
        transaction.owner = owner
        transaction.is_salary = is_salary
        transaction.name = name
        return transaction

    def __str__(self):
        return "{0} on {1}".format(self.amount, self.date)

class RecurringTransaction(Transaction):
    DAILY = 'DA'
    WEEKLY = 'WK'
    MONTHLY = 'MO'
    ANNUALLY = 'AN'
    
    BASE_PERIOD_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (ANNUALLY, 'Annually')
    )

    BASE_PERIOD_NAMES = {
        DAILY: 'day',
        WEEKLY: 'week',
        MONTHLY: 'month',
        ANNUALLY: 'year',
    }

    RRULE_MAPPINGS = {
        DAILY: rrule.DAILY,
        WEEKLY: rrule.WEEKLY,
        MONTHLY: rrule.MONTHLY,
        ANNUALLY: rrule.YEARLY
    }

    start_date = models.DateField(help_text='Use dd/mm/yyyy format')
    end_date = models.DateField(null=True, blank=True, help_text='Optional. Use dd/mm/yyyy format')
    base_period = models.CharField(max_length=2, choices=BASE_PERIOD_CHOICES, blank=False)
    frequency = models.IntegerField()

    def __str__(self):
        if self.base_period == "" or self.base_period == None:
            return ""
        return "{0} {1}".format(self.amount, self.get_frequency_str())

    def get_frequency_str(self):
        inflect_engine = inflect.engine()
        if self.frequency == 1:
            return "every {1}".format(self.amount, self.BASE_PERIOD_NAMES[self.base_period])
        else:
            return "every {1} {2}".format(self.amount, self.frequency, inflect_engine.plural(self.BASE_PERIOD_NAMES[self.base_period]))

    def get_dates(self, force_end_date = None):
        end_date = None
        if force_end_date != None and self.end_date != None:
            end_date = min(force_end_date, self.end_date)
        elif force_end_date != None and self.end_date == None:
            end_date = force_end_date
        else:
            end_date = date.max

        rule = self.get_rrule(end_date)
        return list(rule)

    def get_rrule(self, end_date):
        return rrule.rrule(self.RRULE_MAPPINGS[self.base_period], dtstart=self.start_date, until=end_date, interval=self.frequency)
