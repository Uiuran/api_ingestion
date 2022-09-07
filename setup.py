from setuptools import setup, find_packages


setup(
    name='ingestion',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
    "requests",
    "backoff",
    "ratelimit",
    "boto3",
    "pynamodb",
    "pytest",
    "troposphere",
    "zappa"
    ]
)
