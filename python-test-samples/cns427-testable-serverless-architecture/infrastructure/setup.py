"""Setup for infrastructure package."""

from setuptools import find_packages, setup

setup(
    name='cns427-infrastructure',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'aws-cdk-lib>=2.100.0',
        'constructs>=10.0.0',
    ],
)
