import string
from datetime import datetime
import random
import pprint

from rdflib import SH, RDF, Graph, URIRef, XSD, BNode, Literal

person = "data//person_shape.ttl"
person2 = "data//person_shape2.ttl"
person3 = "data//person_shape3.ttl"
xone_example = "data//xone_example.ttl"
and_example = "data//and_example.ttl"
or_example = "data//or_example.ttl"
equals_example = "data//equals_example.ttl"
less_than_example = "data//less_than_example.ttl"

shape = Graph()
shape.parse(xone_example)

COUNTER = 100


# node shapes: subject in a triple with sh:property predicate and not an object in a triple with sh:property predicate
def find_node_shapes(shapes_graph):
    node_shapes = {s for s in shapes_graph.subjects(None, SH.NodeShape)}
    return node_shapes

def find_independent_node_shapes(shapes_graph):
    node_shapes = find_node_shapes(shapes_graph)
    node_shapes_that_objects_of_sh_node = {s for s in shapes_graph.objects(None, SH.node)}
    print(node_shapes - node_shapes_that_objects_of_sh_node)
    return node_shapes - node_shapes_that_objects_of_sh_node

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
            less_than_dict = sh_properties.get(less_than, {})
            less_than_dict[SH.path] = less_than
            if not less_than_dict.get(SH.datatype) and d.get(SH.datatype):
                less_than_dict[SH.datatype] = d.get(SH.datatype)
            sh_properties[less_than] = less_than_dict
            min_constraint = d.get(SH.minInclusive, d.get(SH.minExclusive))
            if min_constraint:
                less_than_dict[SH.minInclusive] = min_constraint

        less_than_or_equals = d.get(SH.lessThanOrEquals)
        if less_than_or_equals and not sh_properties.get(less_than_or_equals):
            less_than_oe_dict = sh_properties.get(less_than_or_equals, {})
            less_than_oe_dict[SH.path] = less_than_or_equals
            if not less_than_oe_dict.get(SH.datatype) and d.get(SH.datatype):
                less_than_oe_dict[SH.datatype] = d.get(SH.datatype)
            sh_properties[less_than_or_equals] = less_than_oe_dict
            min_constraint = d.get(SH.minInclusive, d.get(SH.minExclusive))
            if min_constraint:
                less_than_oe_dict[SH.minInclusive] = min_constraint

    return shape_dictionary


def generate_integer(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                     min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    if min_exclusive:
        if max_exclusive:
            return Literal(random.randrange(int(min_exclusive), int(max_exclusive)))
        elif less_than:
            less_than = min(less_than)
            return Literal(random.randrange(int(min_exclusive), int(less_than)))
        else:
            return Literal(random.randrange(int(min_exclusive), int(min_exclusive) + 5))
    else:
        if max_exclusive:
            return Literal(random.randrange(int(max_exclusive) - 5, int(max_exclusive)))
        elif less_than:
            less_than = min(less_than)
            return Literal(random.randrange(int(less_than) - 5, int(less_than)))
        else:
            return Literal(random.randrange(0, 5))


def generate_decimal(min_exclusive, min_inclusive, max_exclusive, max_inclusive,
                     min_length, max_length, pattern, disjoint, less_than, less_than_or_equals, has_value):
    if min_inclusive:
        if max_inclusive:
            return Literal(random.randrange(int(min_inclusive), int(max_inclusive)))
        elif less_than:
            less_than = min(less_than)
            return Literal(random.randrange(int(min_inclusive), int(less_than)))
        else:
            return Literal(random.randrange(int(min_inclusive), int(min_inclusive) + 5))
    else:
        if max_inclusive:
            return Literal(random.randrange(int(max_inclusive) - 5, int(max_exclusive)))
        elif less_than:
            less_than = min(less_than)
            return Literal(random.randrange(int(less_than) - 5, int(less_than)))
        else:
            return Literal(random.randrange(0, 5))


# generates a random value based on the SH:datatype
def generate_value(datatype, min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                   pattern, equals, disjoint, less_than, less_than_or_equals, has_value):
    if equals:
        return equals
    value = Literal("default_value")
    if datatype == XSD.integer:
        return generate_integer(min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                                pattern, disjoint, less_than, less_than_or_equals, has_value)
    elif datatype == XSD.decimal:
        return generate_decimal(min_exclusive, min_inclusive, max_exclusive, max_inclusive, min_length, max_length,
                                pattern, disjoint, less_than, less_than_or_equals, has_value)
    elif datatype == XSD.boolean:
        return Literal(bool(random.getrandbits(1)))
    elif datatype == XSD.date:
        return Literal(datetime.date())
    # string or not in the if-else
    return Literal("".join(random.choices(string.ascii_letters, k=random.randint(5, 10))))

def dictionary_to_rdf_graph(shape_dictionary, shape_name, result, parent, dictionary,
                            property_pair_constraint_components_parent):
    # list of properties that have a property_pair_constraint_component
    property_pair_constraint_components = []
    # dict of properties that are added from sh:or/and/xone
    node = BNode()
    if shape_name:
        global COUNTER
        node = URIRef("http://example.org/ns#Node" + str(COUNTER))
        COUNTER += 1
        # with SH.description add the name of the shape that this node was generated from
        result.add((node, SH.description, shape_name))

    sh_target_class = shape_dictionary.get(SH.targetClass)
    if sh_target_class:
        result.add((node, RDF.type, sh_target_class))
    # is it same as the target class?
    sh_class = shape_dictionary.get(URIRef(SH + "class"))
    if sh_class:
        result.add((node, RDF.type, sh_class))

    # if there is a sh:xone for this property, choose one of the choices and merge it with the existing properties
    sh_xone = shape_dictionary.get(URIRef(SH + "xone"))
    if sh_xone:
        choice = random.choice(sh_xone)
        # if the shape contains a sh:path, then it is a new property shape. If not, then the new properties should be added to the dict
        sh_path = choice.get(SH.path)
        if sh_path:
            props = shape_dictionary.get("properties", {})
            props[sh_path] = choice
            shape_dictionary["properties"] = props
        else:
            shape_dictionary.update(choice)

    sh_and = shape_dictionary.get(URIRef(SH + "and"))
    if sh_and:
        for choice in sh_and:
            sh_path = choice.get(SH.path)
            if sh_path:
                props = shape_dictionary.get("properties", {})
                props[sh_path] = choice
                shape_dictionary["properties"] = props
            else:
                shape_dictionary.update(choice)

    # if there is a sh:or for this property, choose some of the choices and merge it with the existing properties
    sh_or = shape_dictionary.get(URIRef(SH + "or"))
    if sh_or:
        for choice in random.choices(sh_or):
            sh_path = choice.get(SH.path)
            if sh_path:
                props = shape_dictionary.get("properties", {})
                props[sh_path] = choice
                shape_dictionary["properties"] = props
            else:
                shape_dictionary.update(choice)

    sh_equals = shape_dictionary.get(SH.equals)
    if sh_equals:
        sh_equals = next(result.objects(parent, sh_equals), None)
        if sh_equals is None:
            property_pair_constraint_components_parent.append(shape_dictionary)
            return None

    sh_disjoint = shape_dictionary.get(SH.disjoint)
    if sh_disjoint:
        sh_disjoint = next(result.objects(parent, sh_disjoint), None)
        if not sh_disjoint is None:
            property_pair_constraint_components_parent.append(shape_dictionary)
            return None

    sh_less_than = shape_dictionary.get(SH.lessThan)
    if sh_less_than:
        # sh_less_than = next(result.objects(parent, sh_less_than), None)
        sh_less_than = [o for o in result.objects(parent, sh_less_than)]
        if sh_less_than == 0:
            property_pair_constraint_components_parent.append(shape_dictionary)
            return None

    sh_less_than_or_equals = shape_dictionary.get(SH.lessThanOrEquals)
    if sh_less_than_or_equals:
        sh_less_than_or_equals = [o for o in result.objects(parent, sh_less_than_or_equals)]
        if sh_less_than_or_equals == 0:
            property_pair_constraint_components_parent.append(shape_dictionary)
            return None

    sh_datatype = shape_dictionary.get(SH.datatype)
    sh_min_exclusive = shape_dictionary.get(SH.minExclusive)
    sh_min_inclusive = shape_dictionary.get(SH.minInclusive)
    sh_max_exclusive = shape_dictionary.get(SH.maxExclusive)
    sh_max_inclusive = shape_dictionary.get(SH.maxInclusive)
    sh_min_length = shape_dictionary.get(SH.minLength)
    sh_max_length = shape_dictionary.get(SH.maxLength)
    sh_pattern = shape_dictionary.get(SH.pattern)
    sh_has_value = shape_dictionary.get(SH.hasValue)
    sh_in = shape_dictionary.get(URIRef(SH + "in"))
    sh_node = shape_dictionary.get(SH.node)

    properties = shape_dictionary.get("properties")
    if properties:
        for key, value in properties.items():
            # the min and max count of the props that are generated
            sh_min_count = int(value.get(SH.minCount, "1"))
            sh_max_count = int(value.get(SH.maxCount, sh_min_count))
            for i in range(0, random.randint(sh_min_count, sh_max_count)):
                generated_prop = dictionary_to_rdf_graph(value, None, result, node, dictionary,
                                                         property_pair_constraint_components)
                if generated_prop is not None:
                    result.add((node, key, generated_prop))
                else:
                    break

        for value in property_pair_constraint_components:
            sh_min_count = int(value.get(SH.minCount, "1"))
            sh_max_count = int(value.get(SH.maxCount, sh_min_count))
            for i in range(0, random.randint(sh_min_count, sh_max_count)):
                generated_prop = dictionary_to_rdf_graph(value, None, result, node, dictionary, [])
                result.add((node, value.get(SH.path), generated_prop))
        return node
    elif sh_in:
        return random.choice(sh_in)
    elif sh_node:
        # if the property is described by a node, generate a node and add it
        return dictionary_to_rdf_graph(dictionary.get(sh_node), sh_node, result, None, dictionary, [])
    return generate_value(sh_datatype, sh_min_exclusive, sh_min_inclusive, sh_max_exclusive, sh_max_inclusive,
                          sh_min_length, sh_max_length, sh_pattern, sh_equals, sh_disjoint, sh_less_than,
                          sh_less_than_or_equals, sh_has_value)


def generate_dictionary_from_shapes_graph(shapes_graph):
    node_shapes = find_node_shapes(shapes_graph)
    dictionary = {}
    for n in node_shapes:
        dictionary[n] = shape_to_dictionary(n, shapes_graph, [])
    return dictionary


def generate_rdf_graph(shapes_graph, dictionary, number_of_samples):
    result_graph = Graph()
    independent_node_shapes = find_independent_node_shapes(shapes_graph)
    for key in independent_node_shapes:
        for i in range(0, number_of_samples):
            dictionary_to_rdf_graph(dictionary[key], key, result_graph, None, dictionary, [])
    return result_graph


dictionary = generate_dictionary_from_shapes_graph(shape)
pprint.PrettyPrinter(indent=0, width=30).pprint(dictionary)
graph = generate_rdf_graph(shape, dictionary, 1)
print("GRAPH")
print(graph.serialize(format="ttl"))
pprint.PrettyPrinter(indent=0, width=30).pprint(dictionary)