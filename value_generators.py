import csv
import random
import time

from exrex import *
from exrex import _randone
from rdflib import XSD, Literal, URIRef

from datetime import date
from dateutil.relativedelta import relativedelta


def get_array_from_csv(file_name):
    results = []
    with open(file_name, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)  # change contents to floats
        for row in reader:  # each row is a list
            results = results + row
    return results


schema = 'http://schema.org/'
values_dict = {'streetAddress': get_array_from_csv('namespaces//street_name.csv'),
               'givenNameMale': get_array_from_csv('namespaces//male_first_name.csv'),
               'givenNameFemale': get_array_from_csv('namespaces//female_first_name.csv'),
               'familyName': get_array_from_csv('namespaces//surnames.csv'),
               'gender': ['male', 'female', 'non-binary'],
               'jobTitle': get_array_from_csv('namespaces//job_title.csv'),
               'bookAward': ["Nobel Prize in Literature", "Pulitzer Prize", "Man Booker Prize", "National Book Award",
                             "Caldecott Medal", "Newbery Medal", "Hugo Award", "Nebula Award",
                             "National Book Critics Circle Award", "PEN/Faulkner Award for Fiction",
                             "Costa Book Awards",
                             "The Giller Prize", "The Women's Prize for Fiction", "The Edgar Allan Poe Awards",
                             "The Agatha Awards", "The James Tait Black Memorial Prize",
                             "The National Poetry Series", "The Bram Stoker Awards", "The Cervantes Prize",
                             "The O. Henry Awards"],
               'bookGenre': get_array_from_csv('namespaces//book_genre.csv'),
               'bookTitle': get_array_from_csv("namespaces//book_titles.csv"),
               'movieGenre': get_array_from_csv('namespaces//movie_genre.csv'),
               'movieAward': get_array_from_csv('namespaces//movie_awards.csv'),
               'movieTitle': get_array_from_csv('namespaces//movie_titles.csv')
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
    length = None
    if min_length or max_length:
        if not min_length and max_length:
            min_length = 8
            max_length = 15
        if not min_length and max_length:
            min_length = 1
        if not max_length and min_length:
            max_length = min_length + 8
        length = random.randint(int(min_length), int(max_length))
    if not pattern:
        pattern = '^([a-zA-Z0-9])*'
    if length:
        strp = ''
        while len(strp) < length:
            strp = strp + _randone(parse(pattern))
        if len(strp) > length:
            strp = strp[:length]
    else:
        strp = _randone(parse(pattern))
    return Literal(strp)


# generates a random value based on the SH:datatype
def generate_value(datatype, min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                   pattern, equals, disjoint, less_than, less_than_or_equals, has_value, path, sh_class):
    cl = str(sh_class).split('/')[-1]
    path = str(path).split('/')[-1]
    # for Person
    if cl == 'Person':
        if 'taxID' == path and not pattern:
            pattern = '[0-9]{9}'
    if cl == 'Book':
        if 'isbn' in path and not pattern:
            pattern = '[0-9]{3}-[0-9]-[0-9]{2}-[0-9]{6}-[0-9]'
        elif 'numberOfPages' in path and not datatype:
            datatype = XSD.integer
        elif 'abridged' in path and not datatype:
            datatype = XSD.boolean
        elif 'bookEdition' in path and not datatype:
            datatype = XSD.integer
    # for all
    if ('date' in path or 'Date' in path) and not datatype:
        datatype = XSD.date
    # person
    elif 'email' in path and not pattern:
        pattern = '([a-z0-9]+[_])*[A-Za-z0-9]+@gmail\.com'
    elif 'telephone' in path and not pattern:
        pattern = '^(\([0-9]{3}\)|[0-9]{3}-)[0-9]{3}-[0-9]{4}$'
    # book

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


def get_predefined_value(sh_path, sh_class, dependencies):
    prop = str(sh_path).split('/')[-1]
    cl = str(sh_class).split('/')[-1]
    values_for_path = values_dict.get(prop)
    # for Person
    if cl == 'Person':
        gender = URIRef(schema + 'gender')
        given_name = URIRef(schema + 'givenName')
        family_name = URIRef(schema + 'familyName')
        name = URIRef(schema + 'name')
        email = URIRef(schema + 'email')
        if prop == 'additionalName' or prop == 'givenName':
            gender = str(dependencies.get(gender, ["none"])[0])
            if gender == 'female':
                return Literal(random.choice(values_dict.get('givenNameFemale')))
            elif gender == 'male':
                return Literal(random.choice(values_dict.get('givenNameMale')))
            else:
                return Literal('dummyname')
        if prop == 'email':
            given_name = dependencies.get(given_name)
            family_name = dependencies.get(family_name)
            name = dependencies.get(name)
            if given_name and family_name:
                return Literal(given_name[0].lower() + "_" + family_name[0].lower() + "@gmail.com")
            elif name:
                email = ""
                for p in name[0].split(' '):
                    email = email + p.lower()
                return Literal(email + "@gmail.com")
            else:
                return Literal('dummyemail')
        if prop == 'familyName':
            return Literal(random.choice(values_dict.get('familyName')))
        if prop == 'name':
            gender = str(dependencies.get(gender, ["none"])[0])
            if gender == 'female':
                return Literal(random.choice(values_dict.get('givenNameFemale')) + " " + random.choice(values_dict.get('familyName')))
            elif gender == 'male':
                return Literal(random.choice(values_dict.get('givenNameMale')) + " " + random.choice(values_dict.get('familyName')))
            else:
                return Literal('dummyname')
        if prop == 'address':
            return Literal("no. " + str(random.randint(1, 100)) + " " + random.choice(values_dict.get('streetAddress')))
        if prop == 'gender':
            return Literal(random.choice(values_dict.get('gender')))
        if prop == 'jobTitle':
            return Literal(random.choice(values_dict.get('jobTitle')))
        # award?
        # place?
    elif cl == 'Book':
        if prop == 'name':
            return Literal(random.choice(values_dict.get("bookTitle")))
        if prop == 'award':
            return Literal(random.choice(values_dict.get('bookAward')))
        if prop == 'genre':
            return Literal(random.choice(values_dict.get('bookGenre')))
        # if prop == 'name':
        #     return Literal(random.choice(values_dict.get('bookName')))
    elif cl == "Movie":
        if prop == 'name':
            return Literal(random.choice(values_dict.get("movieTitle")))
        if prop == 'award':
            return Literal(random.choice(values_dict.get('movieAward')))
        if prop == 'genre':
            return Literal(random.choice(values_dict.get('movieGenre')))
    return None
