from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    description = f.read()

setup(
    name='rdf_graph_gen',
    version='1.1.2',
    description = 'Synthetic RDF graph generator based on SHACL constraints.',
    long_description = description,
    long_description_content_type = 'text/markdown',
    packages=find_packages(),
    package_data={'rdf_graph_gen': ['datasets/*.csv']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'genrdf = rdf_graph_gen.script:main',
        ],
    },
)
