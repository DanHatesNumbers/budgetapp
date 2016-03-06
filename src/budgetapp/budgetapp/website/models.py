from django.db import models
from dateutil import relativedelta
import inflect

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True

class OneOffTransaction(Transaction):
    date = models.DateField()

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

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    base_period = models.CharField(max_length=2, choices=BASE_PERIOD_CHOICES, blank=False)
    frequency = models.IntegerField()

    def __str__(self):
        if self.base_period == "" or self.base_period == None:
            return ""
        inflect_engine = inflect.engine()
        if self.frequency == 1:
            return "{0} every {1}".format(self.amount, self.BASE_PERIOD_NAMES[self.base_period])
        else:
            return "{0} every {1} {2}".format(self.amount, self.frequency, inflect_engine.plural(self.BASE_PERIOD_NAMES[self.base_period]))

    def get_dates(self):
        current_date = self.start_date
        end_date = self.end_date if self.end_date != None else date.max
        delta = get_relativedelta() 

        while current_date <= self.end_date:
            yield current_date
            current_date = current_date + delta 

    def get_relativedelta(self):
        if self.base_period == self.DAILY:
            return relativedelta.relativedelta(days=self.frequency)
        elif self.base_period == self.WEEKLY:
            return relativedelta.relativedelta(weeks=self.frequency)
        elif self.base_period == self.MONTHLY:
            return relativedelta.relativedelta(months=self.frequency)
        elif self.base_period == self.QUARTERLY:
            return relativedelta.relativedelta(months=3*self.frequency)
        else:
            return relativedelta.relativedelta(years=self.frequency)
