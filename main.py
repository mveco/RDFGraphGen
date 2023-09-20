import string
from datetime import datetime
import random
import pprint

from rdflib import SH, RDF, Graph, URIRef, Namespace, XSD, BNode, Literal

person = "data//person_shape.ttl"
person2 = "data//person_shape2.ttl"
xone_example = "data//xone_example.ttl"
and_example = "data//and_example.ttl"
or_example = "data//or_example.ttl"
equals_example = "data//equals_example.ttl"
less_than_example = "data//less_than_example.ttl"

shape = Graph()
shape.parse(person)


# node shapes: subject in a triple with sh:property predicate and not an object in a triple with sh:property predicate
def find_node_shapes(shape):
    subjects = {s for s in shape.subjects(None, SH.NodeShape)}
    # objects = {o for o in shape.objects(None, SH.property)}
    return subjects


# given a rdf list, it returns a python list containing the items in the RDF list.
def get_values_from_list(start, shape):
    items = []
    first = next(shape.objects(start, RDF.first))
    items.append(first)
    rest = next(shape.objects(start, RDF.rest))
    if rest == RDF.nil:
        return items
    else:
        return items + get_values_from_list(rest, shape)


# given a rdf list of shapes, it returns a python list containing the dictionaries for each shape in the rdf list
def get_values_from_property_list(start, shape):
    items = []
    first = next(shape.objects(start, RDF.first))
    items.append(subject_to_dictionary(first, shape, []))
    rest = next(shape.objects(start, RDF.rest))
    if rest == RDF.nil:
        return items
    else:
        return items + get_values_from_property_list(rest, shape)


# given a subject, build a dictionary of all the triples it participates in
def subject_to_dictionary(subject, shape, property_pair_constraint_components_parent):
    triples = shape.triples((subject, None, None))
    # all property pair constraint components that are a sh:property for this subject are stored in here
    property_pair_constraint_components = []
    # a dictionary containing all triples for the current subject
    properties = {}
    subject_dictionary = {}
    for s, p, o in triples:
        if p == SH.property:
            # if the property is a SH:property, then the object is a blank node, which st the same time is a subject in a triple with SH:path property.
            # the subject in the second triple will be the key in the dictionary, and the remaining properties and objects will be added in a dictionary
            property_path = next(shape.objects(o, SH.path))
            # if there is allready an entry for this property, upadete its dict instead of overriding it
            property_dict = properties.get(property_path, {})
            property_dict.update(subject_to_dictionary(o, shape, property_pair_constraint_components))
            properties[property_path] = property_dict
            # in the property_dictionary will be kept all of the data for the new path
        elif p == URIRef(SH + "in"):
            subject_dictionary[p] = get_values_from_list(o, shape)
        elif p == URIRef(SH + "or") or p == URIRef(SH + "and") or p == URIRef(SH + "xone") or p == URIRef(SH + "not"):
            subject_dictionary[p] = get_values_from_property_list(o, shape)
        else:
            # add all dicts that have a Property Pair Constraint Component to be changed additionaly
            if p == SH.lessThan or p == SH.lessThanOrEquals or p == SH.equals or p == SH.disjoint:
                property_pair_constraint_components_parent.append(subject_dictionary)
            subject_dictionary[p] = o
    # add proprties dictionary only if the node has properties
    if bool(properties):
        subject_dictionary["properties"] = properties

    # fixes the dependencies caused by Property Pair Constraint Components
    for d in property_pair_constraint_components:
        # if there is a sh:equals predicate in this component, and it doesnt exist in the dict, add it
        equals = d.get(SH.equals)
        if equals and not properties.get(SH.equals):
            properties[equals] = {SH.path: equals}

        # if there is a sh:disjoint predicate in this component, and it doesnt exist in the dict, add it
        disjoint = d.get(SH.disjoint)
        if disjoint and not properties.get(SH.disjoint):
            properties[disjoint] = {SH.path: disjoint}

        # if there is a sh:lessThan predicate in this component, and it doesnt exist in the dict, add it.
        # if the property with sh:lessThan constraint has a sh:minInclusive/sh:minExclusive constraint,
        # the constraint should be added to the property that it points to.
        less_than = d.get(SH.lessThan)
        if less_than and not properties.get(less_than):
            properties[less_than] = {SH.path: less_than}
            min_constraint = d.get(SH.minInclusive, d.get(SH.minExclusive))
            if min_constraint:
                ltproperty = properties.get(less_than)
                ltproperty[SH.minInclusive] = min_constraint

    return subject_dictionary


# generates a random value based on the SH:datatype
def generate_value(datatype, min_inclusive, max_inclusive, min_length, max_length, less_than):
    if datatype == XSD.integer:
        if less_than:
            return Literal(random.randint(int(min_inclusive), int(less_than)))
        return Literal(random.randint(int(min_inclusive), int(max_inclusive)))
    if datatype == XSD.decimal:
        if less_than:
            return Literal(random.uniform(int(min_inclusive), int(less_than)))
        return Literal(random.uniform(int(min_inclusive), int(max_inclusive)))
    if datatype == XSD.boolean:
        return Literal(bool(random.getrandbits(1)))
    if datatype == XSD.date:
        return Literal(datetime.date())
    lit = Literal("".join(random.choices(string.ascii_letters, k=random.randint(min_length, max_length))))
    if less_than:
        while lit < str(less_than):
            # print("str " + str(lit))
            lit = Literal("".join(random.choices(string.ascii_letters, k=random.randint(min_length, max_length))))
    return lit


def generate_dictionary(shape):
    nodes = find_node_shapes(shape)
    dictionary = {}
    for n in nodes:
        dictionary[n] = subject_to_dictionary(n, shape, [])
    return dictionary


def generate_graph(dictionary):
    result = Graph()
    for key, value in dictionary.items():
        generate_property(value, result, key, dictionary, None, [])
    return result


dictionary = generate_dictionary(shape)
pprint.PrettyPrinter(indent=0, width=30).pprint(dictionary)
# graph = generate_graph(dictionary)
# print("GRAPH")
# print(graph.serialize(format="ttl"))
