import csv
import random
import time

from exrex import *
from exrex import _randone
from rdflib import XSD, Literal

from datetime import date
from dateutil.relativedelta import relativedelta


def get_array_from_csv(file_name):
    results = []
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)  # change contents to floats
        for row in reader:  # each row is a list
            results = results + row
    return results


schema = 'http://schema.org/'
values_dict = {'streetAddress': get_array_from_csv('namespaces//street_name.csv'),
               'firstName': get_array_from_csv('namespaces//female_first_name.csv') +
                            get_array_from_csv('namespaces//male_first_name.csv'),
               'lastName': get_array_from_csv('namespaces//surnames.csv'),
               'jobTitle': get_array_from_csv('namespaces//job_title.csv'),
               'award': ["Nobel Prize in Literature", "Pulitzer Prize", "Man Booker Prize", "National Book Award",
                         "Caldecott Medal", "Newbery Medal", "Hugo Award", "Nebula Award",
                         "National Book Critics Circle Award", "PEN/Faulkner Award for Fiction", "Costa Book Awards",
                         "The Giller Prize", "The Women's Prize for Fiction", "The Edgar Allan Poe Awards",
                         "The Agatha Awards", "The James Tait Black Memorial Prize",
                         "The National Poetry Series", "The Bram Stoker Awards", "The Cervantes Prize",
                         "The O. Henry Awards"],
               'genre': get_array_from_csv('namespaces//book_genre.csv')

               }


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


def generate_date(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                  min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):

    if not min_inclusive:
        min_inclusive = date.fromisoformat('1970-07-07')
    if less_than and len(less_than) > 0:
        max_inclusive = date.fromisoformat(min(less_than))
        if min_inclusive > max_inclusive:
            min_inclusive = add_to_date(str(max_inclusive), -50, 0, 0)
    if not max_inclusive:
        max_inclusive = add_to_date(str(min_inclusive), 50, 10, 5)
    return get_date_between_two_dates(str(min_inclusive), str(max_inclusive))


def generate_integer(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                     min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    # will assume than
    if min_exclusive or max_exclusive or less_than:
        if not min_exclusive:
            min_exclusive = 0
        if less_than and len(less_than) > 0:
            max_exclusive = min(less_than)
            if not min_exclusive:
                min_exclusive = max_exclusive - 15
        if not max_exclusive:
            max_exclusive = min_exclusive + 15
        return Literal(random.randrange(int(min_exclusive), int(max_exclusive)))

    if not min_inclusive:
        min_inclusive = 0
    if less_than_or_equals and len(less_than_or_equals) > 0:
        max_inclusive = min(less_than_or_equals)
        if not min_inclusive:
            min_inclusive = max_inclusive - 15
    if not max_inclusive:
        max_inclusive = min_inclusive + 15
    return Literal(random.randint(int(min_inclusive), int(max_inclusive)))


def generate_decimal(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                     min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    if not min_inclusive:
        min_inclusive = 0
    if less_than_or_equals and len(less_than_or_equals) > 0:
        max_inclusive = min(less_than_or_equals)
        if min_inclusive > max_inclusive:
            min_inclusive = max_inclusive - 15
    if not max_inclusive:
        max_inclusive = min_inclusive + 15
    return Literal(random.uniform(int(min_inclusive), int(max_inclusive)))


def generate_string(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                    min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    if not min_length:
        min_length = 8
    if not max_length:
        max_length = min_length + 8
    if not pattern:
        pattern = '^([a-zA-Z0-9])*'
    length = random.randint(min_length, max_length)
    return Literal(_randone(parse(pattern), length))


# generates a random value based on the SH:datatype
def generate_value(datatype, min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                   pattern, equals, disjoint, less_than, less_than_or_equals, has_value, path, sh_class):
    #for all
    if 'date' in path and not datatype:
        datatype = XSD.date
    # person
    elif 'email' in path and not pattern:
        pattern = '([a-z0-9]+[_])*[A-Za-z0-9]+@gmail\.com'
    elif 'telephone' in path and not pattern:
        pattern = '^(\([0-9]{3}\)|[0-9]{3}-)[0-9]{3}-[0-9]{4}$'
    # book
    elif 'isbn' in path and not pattern:
        pattern = '[0-9]{3}-[0-9]-[0-9]{2}-[0-9]{6}-[0-9]'
    elif 'numberOfPages' in path and not datatype:
        datatype = XSD.integer

    if equals:
        return equals
    if datatype == XSD.integer:
        return generate_integer(min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                                pattern, disjoint, less_than, less_than_or_equals, has_value)
    elif datatype == XSD.decimal:
        return generate_decimal(min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                                pattern, disjoint, less_than, less_than_or_equals, has_value)
    elif datatype == XSD.boolean:
        return Literal(bool(random.getrandbits(1)))
    elif datatype == XSD.date:
        return Literal(generate_date(min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                                     pattern, disjoint, less_than, less_than_or_equals, has_value))
    # string or not in the if-else
    return generate_string(min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                           pattern, disjoint, less_than, less_than_or_equals, has_value)


def get_predefined_value(sh_path, sh_class):
    print(sh_class)
    prop = str(sh_path).split('/')[-1]
    values_for_path = values_dict.get(prop)
    if values_for_path:
        return Literal(random.choice(values_for_path))
    elif prop == 'additionalName' or prop == 'givenName':
        return Literal(random.choice(values_dict.get('firstName')))
    elif prop == 'addressCountry':
        return Literal('United States of America')
    elif prop == 'familyName':
        return Literal(random.choice(values_dict.get('lastName')))
    return None
