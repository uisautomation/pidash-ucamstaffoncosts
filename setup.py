from setuptools import setup, find_packages

setup(
    name='salaries',
    packages=find_packages(),
    package_data={'ucamstaffoncosts': ['data/*.yaml']},
    install_requires=[
        'pyyaml',
    ]
)
