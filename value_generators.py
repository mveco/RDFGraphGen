import csv
import math
import random
from exrex import *
from exrex import _randone
from rdflib import XSD, Literal, URIRef
from datetime import date, datetime
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
               'movieGenre': get_array_from_csv('namespaces/movie_genre.csv'),
               'movieAward': get_array_from_csv('namespaces/movie_awards.csv'),
               'movieTitle': get_array_from_csv('namespaces//movie_titles.csv')
               }


def getBookFormat():
    return URIRef(schema + random.choice(["AudiobookFormat", "EBook", "GraphicNovel", "Hardcover", "Paperback"]))


def get_date_between_two_dates(date1, date2):
    # date1 = date.fromisoformat(date1)
    # date2 = date.fromisoformat(date2)

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
    # date1 = date.fromisoformat(date1)
    time_addition = relativedelta(days=days, months=months, years=years)
    return time_addition + date1


def generate_date(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                  min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    min_date, max_date = None, None
    if min_inclusive or min_exclusive:
        min_date = date.fromisoformat(min_inclusive) if min_inclusive else add_to_date(
            date.fromisoformat(min_exclusive), 0, 0, +1)
    if max_inclusive or max_exclusive:
        max_date = date.fromisoformat(max_inclusive) if max_inclusive else add_to_date(
            date.fromisoformat(max_exclusive), 0, 0, -1)
    if less_than_or_equals and len(less_than_or_equals) > 0:
        max_date = date.fromisoformat(min(less_than_or_equals))
    elif less_than and len(less_than) > 0:
        max_date = date.fromisoformat(min(less_than))
    if max_date:
        if min_date:
            if max_date < min_date:
                raise Exception("A conflicting date definition")
        else:
            min_date = add_to_date(max_date, -50, 0, 0)
    else:
        if not min_date:
            min_date = date.fromisoformat('1970-07-07')
        max_date = add_to_date(min_date, 50, 0, 0)
    return get_date_between_two_dates(min_date, max_date)


def generate_date_old(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                      min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    if not min_inclusive:
        min_inclusive = add_to_date(min_exclusive, 0, 0, -1) if min_exclusive else date.fromisoformat('1970-07-07')
    if (less_than and len(less_than) > 0) or (less_than_or_equals and len(less_than_or_equals) > 0):
        less_than_or_equals = min(less_than_or_equals) if (
                less_than_or_equals and len(less_than_or_equals) > 0) else add_to_date(
            min(less_than), 0, 0, -1)
        max_inclusive = less_than_or_equals if type(less_than_or_equals) is datetime.date \
            else date.fromisoformat(less_than_or_equals)
        print(type(min_inclusive))
        print(type(max_inclusive))
        if min_inclusive > max_inclusive:
            min_inclusive = add_to_date(str(max_inclusive), -50, 0, 0)
    if not max_inclusive:
        max_inclusive = add_to_date(max_exclusive, 0, 0, -1) if max_exclusive else add_to_date(str(min_inclusive), 50,
                                                                                               10, 5)
    return get_date_between_two_dates(str(min_inclusive), str(max_inclusive))


def generate_integer(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                     min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    min_int, max_int = None, None
    if min_inclusive or min_exclusive:
        min_int = min_inclusive if min_inclusive else min_exclusive + 1
    if max_inclusive or max_exclusive:
        max_int = max_inclusive if max_inclusive else max_exclusive - 1
    if less_than_or_equals and len(less_than_or_equals) > 0:
        max_date = min(less_than_or_equals)
    elif less_than and len(less_than) > 0:
        max_int = min(less_than) - 1
    if max_int:
        if min_int:
            if max_int < min_int:
                raise Exception("Conflicting integer constraints")
        else:
            min_int = max_int - 50
    else:
        if not min_int:
            min_int = 1
        max_int = min_int + 50
    return random.randint(min_int, max_int)


def generate_integer_old(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
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


def generate_decimal_old(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
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


def generate_decimal(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                     min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    min_float, max_float = None, None
    if min_inclusive or min_exclusive:
        min_float = min_inclusive if min_inclusive else math.nextafter(min_exclusive, +math.inf)
    if max_inclusive or max_exclusive:
        max_float = max_inclusive if max_inclusive else math.nextafter(max_exclusive, -math.inf)
    if less_than_or_equals and len(less_than_or_equals) > 0:
        max_float = min(less_than_or_equals)
    elif less_than and len(less_than) > 0:
        max_float = math.nextafter(min(less_than), -math.inf)
    if max_float:
        if min_float:
            if max_float < min_float:
                raise Exception("Conflicting float constraints")
        else:
            min_float = max_float - 50
    else:
        if not min_float:
            min_float = 1
        max_float = min_float + 50
    return random.uniform(min_float, max_float)

def generate_string(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                    min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    if min_length:
        if max_length:
            if min_length > max_length:
                raise Exception("Conflicting string constraints")
        else:
            max_length = min_length + 10
    else:
        if max_length:
            min_length = max_length - 5 if max_length > 5 else 0
        else:
            min_length, max_length = 8, 15
    if not pattern:
        pattern = '^([a-zA-Z0-9])*'
    length = random.randint(min_length, max_length)
    strp = ''
    while len(strp) < length:
        strp = strp + _randone(parse(pattern))
    if len(strp) > length:
        strp = strp[:length]
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
            if not min_inclusive:
                min_inclusive = 100
        elif 'abridged' in path and not datatype:
            datatype = XSD.boolean
        elif 'bookEdition' in path and not datatype:
            datatype = XSD.integer
    # for all
    if ('date' in path or 'Date' in path) and not datatype:
        datatype = XSD.date
    # person
    elif 'email' in path and not pattern:
        pattern = '([a-z0-9]+[_])*[A-Za-z0-9]@gmail\.com'
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
            if gender in ('female', 'f', 'fem'):
                return Literal(random.choice(values_dict.get('givenNameFemale')))
            elif gender in ('male', 'm'):
                return Literal(random.choice(values_dict.get('givenNameMale')))
            else:
                return Literal(random.choice(values_dict.get('givenNameMale') + values_dict.get('givenNameFemale')))
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
            elif given_name:
                return Literal(given_name[0].lower() + "_" + str(random.randrange(100, 1000)) + "@gmail.com")

        if prop == 'familyName':
            return Literal(random.choice(values_dict.get('familyName')))
        if prop == 'name':
            gender = str(dependencies.get(gender, ["none"])[0])
            if gender == 'female':
                return Literal(random.choice(values_dict.get('givenNameFemale')) + " " + random.choice(
                    values_dict.get('familyName')))
            elif gender == 'male':
                return Literal(random.choice(values_dict.get('givenNameMale')) + " " + random.choice(
                    values_dict.get('familyName')))
            else:
                return Literal(random.choice(values_dict.get('givenNameMale') + values_dict.get('givenNameFemale')) +
                               " " + random.choice(values_dict.get('familyName')))
        if prop == 'streetAddress':
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
        if prop == 'bookEdition':
            return getBookFormat()
    elif cl == "Movie":
        if prop == 'name':
            return Literal(random.choice(values_dict.get("movieTitle")))
        if prop == 'award':
            return Literal(random.choice(values_dict.get('movieAward')))
        if prop == 'genre':
            return Literal(random.choice(values_dict.get('movieGenre')))
    return None
