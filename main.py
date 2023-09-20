import string
from datetime import datetime
import random
import pprint

from rdflib import SH, RDF, Graph, URIRef, Namespace, XSD, BNode, Literal

person = "data//person_shape.ttl"
person2 = "data//person_shape2.ttl"
person3 = "data//person_shape3.ttl"
xone_example = "data//xone_example.ttl"
and_example = "data//and_example.ttl"
or_example = "data//or_example.ttl"
equals_example = "data//equals_example.ttl"
less_than_example = "data//less_than_example.ttl"

shape = Graph()
shape.parse(person3)


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
def generate_value(datatype, min_count, max_count, min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                   min_length, max_length, pattern, equals, disjoint, less_than, has_value):
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
            lit = Literal("".join(random.choices(string.ascii_letters, k=random.randint(min_length, max_length))))
    return lit


def generate_property(properties, result, shape_name, dictionary, parent, property_pair_constraint_components_parent):
    # list of properties that have a property_pair_constraint_component
    property_pair_constraint_components = []
    # dict of properties that are added from sh:or/and/xone
    node = BNode()
    if shape_name:
        node = URIRef("http://example.org/ns#Node" + str(random.randint(1, 1000)))
        # with SH.description add the name of the shape that this node was generated from
        result.add((node, SH.description, shape_name))

    sh_target_class = properties.get(SH.targetClass)
    if sh_target_class:
        result.add((node, RDF.type, sh_target_class))
    # is it same as the target class?
    sh_class = properties.get(URIRef(SH + "class"))
    if sh_class:
        result.add((node, RDF.type, sh_class))

    # if there is a sh:xone for this property, choose one of the choices and merge it with the existing properties
    sh_xone = properties.get(URIRef(SH + "xone"))
    if sh_xone:
        choice = random.choice(sh_xone)
        # if the shape contains a sh:path, then it is a new property shape. If not, then the new properties should be added to the dict
        sh_path = choice.get(SH.path)
        if sh_path:
            props = properties.get("properties", {})
            props[sh_path] = choice
            properties["properties"] = props
        else:
            properties.update(choice)

    sh_and = properties.get(URIRef(SH + "and"))
    if sh_and:
        for choice in sh_and:
            sh_path = choice.get(SH.path)
            if sh_path:
                props = properties.get("properties", {})
                props[sh_path] = choice
                properties["properties"] = props
            else:
                properties.update(choice)

    # if there is a sh:or for this property, choose some of the choices and merge it with the existing properties
    sh_or = properties.get(URIRef(SH + "or"))
    if sh_or:
        for choice in random.choices(sh_or):
            sh_path = choice.get(SH.path)
            if sh_path:
                props = properties.get("properties", {})
                props[sh_path] = choice
                properties["properties"] = props
            else:
                properties.update(choice)
    #checks if there are any property_pair_constraint_components
    has_pair = properties.get("has_pair")
    sh_equals = properties.get(SH.equals)
    if sh_equals:
        if not has_pair:
            property_pair_constraint_components_parent.append(properties)
            properties["has_pair"] = True
            return None
        else:
            properties.pop("has_pair")

    sh_less_than = properties.get(SH.lessThan)
    if sh_less_than:
        if not has_pair:
            property_pair_constraint_components_parent.append(properties)
            properties["has_pair"] = True
            return None
        else:
            properties.pop("has_pair")

    sh_disjoint = properties.get(SH.disjoint)
    if sh_disjoint:
        if not sh_disjoint:
            property_pair_constraint_components_parent.append(properties)
            properties["has_pair"] = True
            return None
        else:
            properties.pop("has_pair")

    sh_datatype = properties.get(SH.datatype)
    sh_min_count = int(properties.get(SH.minCount, "1"))
    sh_max_count = int(properties.get(SH.maxCount, sh_min_count))
    sh_min_exclusive = properties.get(SH.minExclusive, 100)
    sh_min_inclusive = properties.get(SH.minInclusive, 100)
    sh_max_exclusive = properties.get(SH.maxExclusive, sh_min_inclusive + 100)
    sh_max_inclusive = properties.get(SH.maxInclusive, sh_min_inclusive + 100)
    sh_min_length = properties.get(SH.minLength, 10)
    sh_max_length = properties.get(SH.maxLength, sh_min_length + 10)
    sh_pattern = properties.get(SH.pattern)
    sh_has_value = properties.get(SH.hasValue)

    sh_in = properties.get(URIRef(SH + "in"))
    sh_node = properties.get(SH.node)

    properties = properties.get("properties")
    if properties:
        for key, value in properties.items():
            generated_prop = generate_property(value, result, None, dictionary, node,
                                               property_pair_constraint_components)
            if generated_prop:
                result.add((node, key, generated_prop))

        for value in property_pair_constraint_components:
            generated_prop = generate_property(value, result, None, dictionary, node, property_pair_constraint_components)
            if generated_prop:
                result.add((node, value.get(SH.path), generated_prop))

    elif sh_in:
        return random.choice(sh_in)
    elif sh_node:
        # if the property is described by a node, generate a node and add it
        return generate_property(dictionary.get(sh_node), result, sh_node, dictionary, node, [])
    else:
        return generate_value(sh_datatype, sh_min_count, sh_max_count, sh_min_exclusive, sh_min_inclusive,
                              sh_max_exclusive, sh_max_inclusive, sh_min_length, sh_max_length, sh_pattern, sh_equals,
                              sh_disjoint, sh_less_than, sh_has_value)
    return node


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
graph = generate_graph(dictionary)
print("GRAPH")
print(graph.serialize(format="ttl"))
pprint.PrettyPrinter(indent=0, width=30).pprint(dictionary)
