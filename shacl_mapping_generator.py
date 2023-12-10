from rdflib import SH, RDF, Graph, URIRef, XSD, BNode, Literal


schema = 'http://schema.org/'


def update_dictionary(dict1, dict2):
    for key2, value2 in dict2.items():
        value1 = dict1.get(key2)
        if type(value1) == dict:
            update_dictionary(value1, value2)
        else:
            dict1[key2] = value2


# node shapes: subject in a triple with sh:property predicate and not an object in a triple with sh:property predicate
def find_node_shapes(shapes_graph):
    node_shapes = {s for s in shapes_graph.subjects(None, SH.NodeShape)}
    return node_shapes


def find_independent_node_shapes(shapes_graph):
    node_shapes = find_node_shapes(shapes_graph)
    node_shapes_that_objects_of_sh_node = {s for s in shapes_graph.objects(None, SH.node)}
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
            new_prop_dict = shape_to_dictionary(o, shapes_graph, property_pair_constraint_components)
            update_dictionary(property_dict, new_prop_dict)
            # property_dict.update(shape_to_dictionary(o, shapes_graph, property_pair_constraint_components))
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

def define_dependencies(dictionary):
    t_class = dictionary.get(SH.targetClass)
    if t_class:
        properties = dictionary.get("properties")
        cl = str(t_class).split('/')[-1]
        # for Person
        if cl == 'Person':
            gender = URIRef(schema + 'gender')
            given_name = URIRef(schema + 'givenName')
            family_name = URIRef(schema + 'familyName')
            name = URIRef(schema + 'name')
            email = URIRef(schema + 'email')
            gender_dict = properties.get(gender)
            given_name_dict = properties.get(given_name)
            family_name_dict = properties.get(family_name)
            name_dict = properties.get(name)
            email_dict = properties.get(email)
            if gender_dict and given_name_dict:
                dependency_list = given_name_dict.get('depends_on', [])
                dependency_list.append(gender)
                given_name_dict['depends_on'] = dependency_list
            if gender_dict and name_dict:
                dependency_list = name_dict.get('depends_on', [])
                dependency_list.append(gender)
                name_dict['depends_on'] = dependency_list
            if email_dict:
                dependency_list = email_dict.get('depends_on', [])
                if given_name_dict and family_name_dict:
                    dependency_list.append(given_name)
                    dependency_list.append(family_name)
                elif name_dict:
                    dependency_list.append(name)
                elif given_name_dict:
                    dependency_list.append(given_name)
                email_dict['depends_on'] = dependency_list

def generate_dictionary_from_shapes_graph(shapes_graph):
    node_shapes = find_node_shapes(shapes_graph)
    dictionary = {}
    for n in node_shapes:
        d = shape_to_dictionary(n, shapes_graph, [])
        dictionary[n] = d
        # define_dependencies(d)
    return dictionary
