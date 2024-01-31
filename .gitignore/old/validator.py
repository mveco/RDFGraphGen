from pyshacl import validate


shapes_file = "old_shapes/less_than_example.ttl"
shapes_file_format = 'turtle'

data_file = "old_shapes/less_than_graph.ttl"
data_file_format = 'turtle'

conforms, v_graph, v_text = validate(data_file, shacl_graph=shapes_file,
                                     data_graph_format=data_file_format,
                                     shacl_graph_format=shapes_file_format,
                                     inference='rdfs', debug=False,
                                     serialize_report_graph=True)
print(conforms)
print(v_graph)
print(v_text)

# minInclusive, minExclusive, maxInclusive, maxExclusive work for all datatypes.
#