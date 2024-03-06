from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    description = f.read()

setup(
    name='rdf_shacl_generator',
    version='1.0.2',
    short_description = 'Synthetic RDF graph generator based on SHACL constraints.',
    short_description_content_type = 'text/markdown',
    long_description = description,
    long_description_content_type = 'text/markdown',
    packages=find_packages(),
    package_data={'rdf_shacl_generator': ['datasets/*.csv']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'genrdf = rdf_shacl_generator.script:main',
        ],
    },
)
