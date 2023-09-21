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
def find_node_shapes(shapes_graph):
    node_shapes = {s for s in shapes_graph.subjects(None, SH.NodeShape)}
    return node_shapes


# given a rdf list, it returns a python list containing the items in the RDF list.
def get_list_from_shacl_list(start, shapes_graph):
    _list = []
    first = next(shapes_graph.objects(start, RDF.first))
    _list.append(first)
    rest = next(shapes_graph.objects(start, RDF.rest))
    if rest == RDF.nil:
        return _list
    else:
        return _list + get_list_from_shacl_list(rest, shapes_graph)


# given a rdf list of shapes, it returns a python list containing the dictionaries for each shape in the rdf list
def get_dict_list_from_shacl_list(start, shapes_graph, property_pair_constraint_components):
    items = []
    first = next(shapes_graph.objects(start, RDF.first))
    items.append(shape_to_dictionary(first, shapes_graph, property_pair_constraint_components))
    rest = next(shapes_graph.objects(start, RDF.rest))
    if rest == RDF.nil:
        return items
    else:
        return items + get_dict_list_from_shacl_list(rest, shapes_graph, property_pair_constraint_components)


# given a subject, build a dictionary of all the triples it participates in
def shape_to_dictionary(shape, shapes_graph, property_pair_constraint_components_parent):
    triples = shapes_graph.triples((shape, None, None))
    # all property pair constraint components that are a sh:property for this subject are stored in here
    property_pair_constraint_components = []
    # a dictionary containing all triples for the current subject
    sh_properties = {}
    shape_dictionary = {}
    for s, p, o in triples:
        if p == SH.property:
            # if the property is a SH:property, then the object is a blank node, which st the same time is a subject in a triple with SH:path property.
            # the subject in the second triple will be the key in the dictionary, and the remaining properties and objects will be added in a dictionary
            property_path = next(shapes_graph.objects(o, SH.path))
            # if there is allready an entry for this property, upadete its dict instead of overriding it
            property_dict = sh_properties.get(property_path, {})
            property_dict.update(shape_to_dictionary(o, shapes_graph, property_pair_constraint_components))
            sh_properties[property_path] = property_dict
            # in the property_dictionary will be kept all the data for the new path
        elif p == URIRef(SH + "in"):
            shape_dictionary[p] = get_list_from_shacl_list(o, shapes_graph)
        elif p == URIRef(SH + "or") or p == URIRef(SH + "and") or p == URIRef(SH + "xone") or p == URIRef(SH + "not"):
            shape_dictionary[p] = get_dict_list_from_shacl_list(o, shapes_graph,
                                                                property_pair_constraint_components_parent)
        else:
            # add all dicts that have a Property Pair Constraint Component to be changed additionaly
            if p == SH.lessThan or p == SH.lessThanOrEquals or p == SH.equals or p == SH.disjoint:
                property_pair_constraint_components_parent.append(shape_dictionary)
            shape_dictionary[p] = o
    # add proprties dictionary only if the node has properties
    if bool(sh_properties):
        shape_dictionary["properties"] = sh_properties

    # fixes the dependencies caused by Property Pair Constraint Components
    for d in property_pair_constraint_components:
        # if there is a sh:equals predicate in this component, and it doesnt exist in the dict, add it
        equals = d.get(SH.equals)
        if equals and not sh_properties.get(SH.equals):
            sh_properties[equals] = {SH.path: equals}

        # if there is a sh:disjoint predicate in this component, and it doesnt exist in the dict, add it
        disjoint = d.get(SH.disjoint)
        if disjoint and not sh_properties.get(SH.disjoint):
            sh_properties[disjoint] = {SH.path: disjoint}

        # if there is a sh:lessThan predicate in this component, and it doesnt exist in the dict, add it.
        # if the property with sh:lessThan constraint has a sh:minInclusive/sh:minExclusive constraint,
        # the constraint should be added to the property that it points to.
        less_than = d.get(SH.lessThan)
        if less_than and not sh_properties.get(less_than):
            sh_properties[less_than] = {SH.path: less_than}
            min_constraint = d.get(SH.minInclusive, d.get(SH.minExclusive))
            if min_constraint:
                lt_property = sh_properties.get(less_than)
                lt_property[SH.minInclusive] = min_constraint

        less_than_or_equals = d.get(SH.lessThanOrEquals)
        if less_than_or_equals and not sh_properties.get(less_than_or_equals):
            sh_properties[less_than_or_equals] = {SH.path: less_than_or_equals}
            min_constraint = d.get(SH.minInclusive, d.get(SH.minExclusive))
            if min_constraint:
                ltoe_property = sh_properties.get(less_than_or_equals)
                ltoe_property[SH.minExclusive] = min_constraint

    return shape_dictionary


# generates a random value based on the SH:datatype
def generate_value(datatype, min_count, max_count, min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                   min_length, max_length, pattern, equals, disjoint, less_than, has_value):
    # values = []
    # for i in range(min_count, max_count):

    if equals:
        return equals

    value = Literal("default_value")
    if datatype == XSD.integer:
        if min_exclusive:
            if max_exclusive:
                value = Literal(random.randrange(int(min_exclusive), int(max_exclusive)))
            elif less_than:
                value = Literal(random.randrange(int(min_exclusive), int(less_than)))
            else:
                value = Literal(random.randrange(int(min_exclusive), int(min_exclusive) + 5))
        else:
            if max_exclusive:
                value = Literal(random.randrange(int(max_exclusive) - 5, int(max_exclusive)))
            elif less_than:
                value = Literal(random.randrange(int(less_than) - 5, int(less_than)))
            else:
                value = Literal(random.randrange(0, 5))

    elif datatype == XSD.decimal:
        if min_inclusive:
            if max_inclusive:
                value = Literal(random.randrange(int(min_inclusive), int(max_inclusive)))
            elif less_than:
                value = Literal(random.randrange(int(min_inclusive), int(less_than)))
            else:
                value = Literal(random.randrange(int(min_inclusive), int(min_inclusive) + 5))
        else:
            if max_inclusive:
                value = Literal(random.randrange(int(max_inclusive) - 5, int(max_exclusive)))
            elif less_than:
                value = Literal(random.randrange(int(less_than) - 5, int(less_than)))
            else:
                value = Literal(random.randrange(0, 5))

    elif datatype == XSD.boolean:
        value = Literal(bool(random.getrandbits(1)))

    elif datatype == XSD.date:
        value = Literal(datetime.date())

    elif datatype == XSD.string:
        value = Literal("".join(random.choices(string.ascii_letters, k=random.randint(5, 10))))

    # if disjoint and value == disjoint:
    #     i = i - 1
    #     continue
    # values.append(value)

    if has_value:
        value = has_value

    return value


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
    # checks if there are any property_pair_constraint_components
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
    sh_min_exclusive = properties.get(SH.minExclusive)
    sh_min_inclusive = properties.get(SH.minInclusive)
    sh_max_exclusive = properties.get(SH.maxExclusive)
    sh_max_inclusive = properties.get(SH.maxInclusive)
    sh_min_length = properties.get(SH.minLength)
    sh_max_length = properties.get(SH.maxLength)
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
                result.add((node, value.get(SH.path), generated_prop))

        for value in property_pair_constraint_components:
            generated_prop = generate_property(value, result, None, dictionary, node,
                                               property_pair_constraint_components)
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


def generate_dictionary_from_shapes_graph(shapes_graph):
    node_shapes = find_node_shapes(shapes_graph)
    dictionary = {}
    for n in node_shapes:
        dictionary[n] = shape_to_dictionary(n, shapes_graph, [])
    return dictionary


def generate_rdf_graph(dictionary):
    result_graph = Graph()
    for key, value in dictionary.items():
        generate_property(value, result_graph, key, dictionary, None, [])
    return result_graph


dictionary = generate_dictionary_from_shapes_graph(shape)
pprint.PrettyPrinter(indent=0, width=30).pprint(dictionary)
graph = generate_rdf_graph(dictionary)
print("GRAPH")
print(graph.serialize(format="ttl"))
pprint.PrettyPrinter(indent=0, width=30).pprint(dictionary)
