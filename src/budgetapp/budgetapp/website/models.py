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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User)

    class Meta:
        abstract = True

class OneOffTransaction(Transaction):
    date = models.DateField()

    @classmethod
    def create(cls, transaction_date, amount, owner, name = None):
        transaction = cls()
        transaction.date = transaction_date
        transaction.amount = amount
        transaction.owner = owner
        transaction.name = name
        return transaction

    def __str__(self):
        return "{0} on {1}".format(self.amount, self.date)

class RecurringTransaction(Transaction):
    DAILY = 'DA'
    WEEKLY = 'WK'
    MONTHLY = 'MO'
    QUARTERLY = 'QR'
    YEARLY = 'YR'
    
    BASE_PERIOD_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quartly'),
        (YEARLY, 'Yearly')
    )

    BASE_PERIOD_NAMES = {
        DAILY: 'day',
        WEEKLY: 'week',
        MONTHLY: 'month',
        QUARTERLY: 'quarter',
        YEARLY: 'year',
    }

    RRULE_MAPPINGS = {
        DAILY: rrule.DAILY,
        WEEKLY: rrule.WEEKLY,
        MONTHLY: rrule.MONTHLY,
        YEARLY: rrule.YEARLY
    }

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    base_period = models.CharField(max_length=2, choices=BASE_PERIOD_CHOICES, blank=False)
    frequency = models.IntegerField()
    is_salary = models.BooleanField(default=False)

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
        if self.base_period == self.QUARTERLY:
            return rrule.rrule(MONTHLY, dtstart=self.start_date, until=end_date, interval=self.frequency*3)
        else:
            return rrule.rrule(self.RRULE_MAPPINGS[self.base_period], dtstart=self.start_date, until=end_date, interval=self.frequency)
