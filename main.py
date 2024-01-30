from rdf_graph_generator import *

person = "old_shapes//person_shape.ttl"
person2 = "old_shapes//person_shape2.ttl"
person3 = "old_shapes//person_shape3.ttl"
xone_example = "old_shapes//xone_example.ttl"
and_example = "old_shapes//and_example.ttl"
or_example = "old_shapes//or_example.ttl"
equals_example = "old_shapes//equals_example.ttl"
less_than_example = "old_shapes//less_than_example.ttl"
movie = "shape_examples//movie_shape.ttl"
book = "shape_examples//book_shape.ttl"
tv_series = "shape_examples//tv_series_shape.ttl"
person_new = "shape_examples//person_shape.ttl"
test = "shape_examples//test_value_generation.ttl"




create_rdf_examples(person_new, 5, "output_file.ttl")
