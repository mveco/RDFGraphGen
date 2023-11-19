import random
from datetime import date

from dateutil.relativedelta import relativedelta
def get_date_between_two_dates(date1, date2):
    date1 = date.fromisoformat(date1)
    date2 = date.fromisoformat(date2)

    days_between = relativedelta(date2, date1).days
    months_between = relativedelta(date2, date1).months
    years_between = relativedelta(date2, date1).years

    increase = random.random()
    new_days = relativedelta(days=int(days_between * increase))
    new_months = relativedelta(months=int(months_between * increase))
    new_years = relativedelta(years=int(years_between * increase))

    between_date = date1 + new_years + new_months + new_days
    return between_date


def add_to_date(date1, years, months, days):
    date1 = date.fromisoformat(date1)
    time_addition = relativedelta(days=days, months=months, years=years)

    return time_addition + date1


print(get_date_between_two_dates('2022-01-01', '1999-01-01'))
print(add_to_date('2000-05-05', 10, -6, -3))
