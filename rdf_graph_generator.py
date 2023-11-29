from copy import deepcopy
import random
import pprint
from rdflib import SH, RDF, Graph, URIRef, XSD, BNode, Literal

from value_generators import *
from shacl_mapping_generator import *

COUNTER = 100


def dictionary_to_rdf_graph(shape_dictionary, shape_name, result, parent, dictionary,
                            property_pair_constraint_components_parent, parent_class):
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

    sh_class = shape_dictionary.get(SH.targetClass)
    if sh_class:
        result.add((node, RDF.type, sh_class))
        parent_class = sh_class
    # is it same as the target class?
    sh_class = shape_dictionary.get(URIRef(SH + "class"))
    if sh_class:
        result.add((node, RDF.type, sh_class))
        parent_class = sh_class

    # if there is a sh:xone for this property, choose one of the choices and merge it with the existing properties
    sh_xone = shape_dictionary.get(URIRef(SH + "xone"))
    if sh_xone:
        # it is copiest so it wont change permanently(needed when generating multiple rdf graphs)
        shape_dictionary = deepcopy(shape_dictionary)
        choice = random.choice(sh_xone)
        # if the shape contains a sh:path, then it is a new property shape. If not, then the new properties should be added to the dict
        sh_path = choice.get(SH.path)
        if sh_path:
            choice = {"properties": {sh_path: choice}}
        update_dictionary(shape_dictionary, choice)
        # shape_dictionary.update(choice)

    sh_and = shape_dictionary.get(URIRef(SH + "and"))
    if sh_and:
        shape_dictionary = deepcopy(shape_dictionary)
        for choice in sh_and:
            sh_path = choice.get(SH.path)
            if sh_path:
                choice = {"properties": {sh_path: choice}}
            update_dictionary(shape_dictionary, choice)

    # if there is a sh:or for this property, choose some of the choices and merge it with the existing properties
    sh_or = shape_dictionary.get(URIRef(SH + "or"))
    if sh_or:
        shape_dictionary = deepcopy(shape_dictionary)
        len_choices = len(sh_or)
        for choice in random.sample(sh_or, random.randint(1, len_choices)):
            sh_path = choice.get(SH.path)
            if sh_path:
                choice = {"properties": {sh_path: choice}}
            update_dictionary(shape_dictionary, choice)

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
        if len(sh_less_than) == 0:
            property_pair_constraint_components_parent.append(shape_dictionary)
            return None

    sh_less_than_or_equals = shape_dictionary.get(SH.lessThanOrEquals)
    if sh_less_than_or_equals:
        sh_less_than_or_equals = [o for o in result.objects(parent, sh_less_than_or_equals)]
        if len(sh_less_than_or_equals) == 0:
            property_pair_constraint_components_parent.append(shape_dictionary)
            return None

    dependencies = {}
    depends_on = shape_dictionary.get("depends_on", []) #[] is to mot check if there are dependencies
    print(depends_on)
    for dep in depends_on:
        val = [o for o in result.objects(parent, dep)]
        if len(val) == 0:
            property_pair_constraint_components_parent.append(shape_dictionary)
            return None
        dependencies[dep] = val
    print(dependencies)
    # if depends_on:
    #     print(depends_on)
    #     depends_on = [o for o in result.objects(parent, depends_on)]
    #     print(depends_on)
    #     if len(depends_on) == 0:
    #         property_pair_constraint_components_parent.append(shape_dictionary)
    #         return None

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
    sh_path = shape_dictionary.get(SH.path)

    properties = shape_dictionary.get("properties")
    if properties:
        for key, value in properties.items():
            # the min and max count of the props that are generated
            sh_min_count = int(value.get(SH.minCount, "1"))
            sh_max_count = int(value.get(SH.maxCount, sh_min_count))
            for i in range(0, random.randint(sh_min_count, sh_max_count)):
                generated_prop = dictionary_to_rdf_graph(value, None, result, node, dictionary,
                                                         property_pair_constraint_components, parent_class)
                if generated_prop is not None:
                    result.add((node, key, generated_prop))
                # else:
                #     break

        while property_pair_constraint_components:
            value = property_pair_constraint_components.pop(0)
            sh_min_count = int(value.get(SH.minCount, "1"))
            sh_max_count = int(value.get(SH.maxCount, sh_min_count))
            for i in range(0, random.randint(sh_min_count, sh_max_count)):
                generated_prop = dictionary_to_rdf_graph(value, None, result, node, dictionary,
                                                             property_pair_constraint_components, parent_class)
                if generated_prop is not None:
                    result.add((node, value.get(SH.path), generated_prop))
                else:
                    break
        return node

    elif sh_in:
        return random.choice(sh_in)
    elif sh_node:
        # if the property is described by a node, generate a node and add it
        return dictionary_to_rdf_graph(dictionary.get(sh_node), sh_node, result, None, dictionary, [], None)
    predefined_value = get_predefined_value(sh_path, parent_class, dependencies)
    if predefined_value:
        return predefined_value
    return generate_value(sh_datatype, sh_min_exclusive, sh_min_inclusive, sh_max_exclusive, sh_max_inclusive,
                          sh_min_length, sh_max_length, sh_pattern, sh_equals, sh_disjoint, sh_less_than,
                          sh_less_than_or_equals, sh_has_value, sh_path, parent_class)


def generate_rdf_graph(shapes_graph, dictionary, number_of_samples):
    result_graph = Graph()
    independent_node_shapes = find_independent_node_shapes(shapes_graph)
    for key in independent_node_shapes:
        for i in range(0, number_of_samples):
            dictionary_to_rdf_graph(dictionary[key], key, result_graph, None, dictionary, [], None)
    return result_graph


def generate_rdf_graphs_from_shacl_constraints(shape_file, number):
    shape = Graph()
    shape.parse(shape_file)
    dictionary = generate_dictionary_from_shapes_graph(shape)
    graph = generate_rdf_graph(shape, dictionary, number)
    return graph
