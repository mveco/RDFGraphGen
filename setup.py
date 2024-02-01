from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='rdf_shacl_generator',
    version='0.1.0',
    packages=find_packages(),
    package_data={'rdf_shacl_generator': ['datasets/*.csv']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'genrdf = rdf_shacl_generator.script:main',
        ],
    },
)
