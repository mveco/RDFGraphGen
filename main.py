from rdflib import Graph

from rdf_graph_generator import *

person = "data//person_shape.ttl"
person2 = "data//person_shape2.ttl"
person3 = "data//person_shape3.ttl"
xone_example = "data//xone_example.ttl"
and_example = "data//and_example.ttl"
or_example = "data//or_example.ttl"
equals_example = "data//equals_example.ttl"
less_than_example = "data//less_than_example.ttl"
movie = "shape_examples//movie_shape.ttl"
book = "shape_examples//book_shape.ttl"
person_new = "shape_examples//person_shape.ttl"


def create_rdf_examples(shape_file, number, output_file):
    shape = Graph()
    shape.parse(shape_file)
    dictionary = generate_dictionary_from_shapes_graph(shape)
    graph = generate_rdf_graph(shape, dictionary, number)
    graph.serialize(destination=output_file)


create_rdf_examples(movie, 6, "output_file.ttl")
