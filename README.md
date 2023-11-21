# RDF_generator
DATASETS:
street names: https://data.amerigeoss.org/dataset/street-names-37fec/resource/d655cc82-c98f-450a-b9bb-63521c870503?view_id=dc32f987-ef87-4ded-964e-22c54b7a0253

sh:nodeKind is not developed

sh:targetNode : any IRI or literal - ignored because this is a multiple rdf graph generator
sh:targetObjectsOf : rdf:Property are ignored because they carry no useful info
sh:targetSubjectsOf : rdf:Property are ignored because they carry no useful info

Each NodeShape has to have a 'a sh:NodeShape' property and object in order to be recognized as a Node shape

- added recognizing when constraints are spread across multiple (property) shapes add summing up all of the constraints in the shapes

sh:severity is ignored because it carries no useful info
sh:deactivated -||-

 SHACL Property Paths are not supported
 
sh:dataype can have multiple vlues, so only these are 
sh:nodeKind is ignored

the properties with a sh:minCount constraint can sometimes have a smaller value than the deined minimum count.
This is because sometimes the rdf generator generates the seme value multiple times. 

-When property1 is sh:lessThan property2, added a functionality that checks it the value for property1 is smaller than all of the values for property 2

TODO: sh:languageIn


For the LogicalConstraintComponents are generated, the graph in changed every time using a copy
For sh:and, all of the options in the list are added to the dictionary
Fot sh:or one or more of the options in the list are added to the dictionary
For sh:xone, only one of the options is added.