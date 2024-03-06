
# Synthetic RDF graph generator based on SHACL constraints.

### rdf_shacl_generator is a Python package that can be used to generate RDF graphs based on SHACL constraints.

The following function can be used to generate RDF data:

__generate_rdf(file1, file2, number_of_entities)__
- file1 is a turtle file that contains SHACL shapes.
- file2 is a turtle file that will store the generated RDF entities
- number_of_entities is the number of RDF entities to be generated.

Link on PyPi: https://pypi.org/project/rdf-shacl-generator/

Link on GitHub: https://github.com/mveco/RDF_generator

Installation: 

```pip install rdf-shacl-generator```

After installation, this package can be used as a command line tool:

```rdfgen file1 file2 number_of_entities```

### Remarks:
- A SHACL shape has to have a 'a sh:NodeShape' property and object in order to be recognized as a Node Shape.
- sh:severity is ignored because it has no useful info.
- SHACL Property Paths are not supported
- sh:datatype can have many different values, not all are recognized.
- sh:nodeKind is ignored
- The triples generated based on properties with a sh:minCount constraint can sometimes have a smaller value than the defined minimum count. This is because sometimes the generator generates the same triple multiple times. 
