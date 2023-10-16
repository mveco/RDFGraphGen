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
               'jobTitle': ['accountant', 'aerospace_engineer', 'aide', 'air_conditioning_installer', 'architect', 'artist',
                       'author',
                       'baker', 'bartender', 'bus_driver', 'butcher', 'career_counselor', 'carpenter',
                       'carpet_installer', 'cashier',
                       'ceo', 'childcare_worker', 'civil_engineer', 'claims_appraiser', 'cleaner', 'clergy', 'clerk',
                       'coach',
                       'community_manager', 'compliance_officer', 'computer_programmer', 'computer_support_specialist',
                       'computer_systems_analyst',
                       'construction_worker', 'cook', 'correctional_officer', 'courier', 'credit_counselor',
                       'customer_service_representative',
                       'data_entry_keyer', 'dental_assistant', 'dental_hygienist', 'dentist', 'designer', 'detective',
                       'director', 'dishwasher',
                       'dispatcher', 'doctor', 'drywall_installer', 'electrical_engineer', 'electrician', 'engineer',
                       'event_planner',
                       'executive_assistant', 'facilities_manager', 'farmer', 'fast_food_worker', 'file_clerk',
                       'financial_advisor',
                       'financial_analyst', 'financial_manager', 'firefighter', 'fitness_instructor',
                       'graphic_designer', 'groundskeeper',
                       'hairdresser', 'head_cook', 'health_technician', 'host', 'hostess', 'industrial_engineer',
                       'insurance_agent',
                       'interior_designer', 'interviewer', 'inventory_clerk', 'it_specialist', 'jailer', 'janitor',
                       'laboratory_technician',
                       'language_pathologist', 'lawyer', 'librarian', 'logistician', 'machinery_mechanic', 'machinist',
                       'maid', 'manager',
                       'manicurist', 'market_research_analyst', 'marketing_manager', 'massage_therapist', 'mechanic',
                       'mechanical_engineer',
                       'medical_records_specialist', 'mental_health_counselor', 'metal_worker', 'mover', 'musician',
                       'network_administrator',
                       'nurse', 'nursing_assistant', 'nutritionist', 'occupational_therapist', 'office_clerk',
                       'office_worker', 'painter',
                       'paralegal', 'payroll_clerk', 'pharmacist', 'pharmacy_technician', 'photographer',
                       'physical_therapist', 'pilot',
                       'plane_mechanic', 'plumber', 'police_officer', 'postal_worker', 'printing_press_operator',
                       'producer', 'psychologist',
                       'public_relations_specialist', 'purchasing_agent', 'radiologic_technician', 'real_estate_broker',
                       'receptionist',
                       'repair_worker', 'roofer', 'sales_manager', 'salesperson', 'school_bus_driver', 'scientist',
                       'security_guard',
                       'sheet_metal_worker', 'singer', 'social_assistant', 'social_worker', 'software_developer',
                       'stocker', 'stubborn',
                       'supervisor', 'taxi_driver', 'teacher', 'teaching_assistant', 'teller', 'therapist',
                       'tractor_operator', 'truck_driver',
                       'tutor', 'underwriter', 'veterinarian', 'waiter', 'waitress', 'welder', 'wholesale_buyer',
                       'writer']
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
