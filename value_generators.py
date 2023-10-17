import csv
import random
import time

from exrex import *
from exrex import _randone
from rdflib import XSD, Literal


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
               'jobTitle': get_array_from_csv('namespaces//job_title.csv')
               }


def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def generate_date(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                  min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    time_format = '%Y-%m-%d'

    if not min_inclusive:
        min_inclusive = time.mktime(time.strptime('2000-01-01', time_format))
    if less_than_or_equals and len(less_than_or_equals) > 0:
        max_inclusive = time.mktime(time.strptime(min(less_than_or_equals), time_format))
        if min_inclusive > max_inclusive:
            min_inclusive = max_inclusive - 300000000
    if not max_inclusive:
        max_inclusive = min_inclusive + 300000000
    min_inclusive = time.strftime(time_format, time.localtime(min_inclusive))
    max_inclusive = time.strftime(time_format, time.localtime(max_inclusive))
    return str_time_prop(str(min_inclusive), str(max_inclusive), time_format, random.random())


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
    print(pattern)
    # will assume than
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
                   pattern, equals, disjoint, less_than, less_than_or_equals, has_value):
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


def get_predefined_value(sh_path):
    prop = str(sh_path).split('/')[-1]
    values_for_path = values_dict.get(prop)
    if values_for_path:
        return Literal(random.choice(values_for_path))
    elif prop == 'name':
        first_name = random.choice(values_dict.get('firstName'))
        # last_name = values_dict.get('lastName')
        last_name = random.choice(values_dict.get('lastName'))
        return Literal(first_name + " " + last_name)
    elif prop == 'aditionalName' or prop == 'givenName':
        return Literal(random.choice(values_dict.get('firstName')))
    elif prop == 'addressCountry':
        return Literal('United States of America')
    elif prop == 'familyName':
        return Literal(random.choice(values_dict.get('lastName')))
    return None
