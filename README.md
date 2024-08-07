# RDFGraphGen: A Synthetic RDF Graph Generator based on SHACL Constraints

This is a Python package which can be used to generate synthetic RDF knowledge graphs, based on SHACL constraints. 

The Shapes Constraint Language (SHACL) is a W3C standard which specifies ways to validate data in RDF graphs, by defining constraining shapes. However, even though the main purpose of SHACL is validation of existing RDF data, in order to solve the problem with the lack of available RDF datasets in multiple RDF-based application development processes, we envisioned and implemented a reverse role for SHACL: we use SHACL shape definitions as a starting point to generate synthetic data for an RDF graph. 

The generation process involves extracting the constraints from the SHACL shapes, converting the specified constraints into rules, and then generating artificial data for a predefined number of RDF entities, based on these rules. The purpose of RDFGraphGen is the generation of small, medium or large RDF knowledge graphs for the purpose of benchmarking, testing, quality control, training and other similar purposes for applications from the RDF, Linked Data and Semantic Web domain.

## Usage

The following function can be used to generate RDF data:

__generate_rdf(input-shape.ttl, output-graph.ttl, number-of-entities)__
- input-shape.ttl is a Turtle file that contains SHACL shapes
- output-graph.ttl is a Turtle file that will store the generated RDF entities
- number-of-entities is the number of RDF entities to be generated

## Installation

RDFGraphGen is available on PyPi: https://pypi.org/project/rdf-graph-gen/

To install it, use:

```pip install rdf-graph-gen```

After installation, this package can be used as a command line tool:

```rdfgen input-shape.ttl output-graph.ttl number-of-entities```

The parameters here are the same as the ones described above.

## Examples
Examples of SHACL shapes based on Schema.org and other types, along with generated synthetic RDF graphs based on these shapes, can be found in the [generated examples](generated_examples/) directory in this repo.

## Publications

* (preprint) Marija Vecovska, Milos Jovanovik. "[RDFGraphGen: A Synthetic RDF Graph Generator based on SHACL Constraints](https://arxiv.org/abs/2407.17941)". arXiv:2407.17941.

## Remarks
- A SHACL shape has to have a 'a sh:NodeShape' property and object in order to be recognized as a Node Shape.
- sh:severity is ignored because it has no useful info.
- SHACL Property Paths are not supported
- sh:datatype can have many different values, not all are recognized.
- sh:nodeKind is ignored
- The triples generated based on properties with a sh:minCount constraint can sometimes have a smaller value than the defined minimum count. This is because sometimes the generator generates the same triple multiple times. 
