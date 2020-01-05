import os
from setuptools import find_packages, setup

# determining the directory containing setup.py
setup_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(setup_path, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    # package information
    name = 'timone',
    packages = find_packages(),
    version = '0.0.2',
    description = 'A lightweight server to handle Git LFS on different storage backends.',
    long_description = readme,
    license = 'MIT',
    url='https://github.com/gstracquadanio/timone.git',
    keywords='',

    # author information
    author = 'Giovanni Stracquadanio',
    author_email = 'dr.stracquadanio@gmail.com',

    # installation info and requirements
    install_requires=[
        "python-dotenv>=0.10.3",
        "falcon>=2.0.0",
        "boto3>=1.10",
        "PyJWT>=1.7.1"
    ],
    setup_requires=[],

    # test info and requirements
    test_suite='tests',
    tests_require=[],

    # package deployment info
    include_package_data=True,
    zip_safe=False,

)
