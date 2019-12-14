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
    version = '0.0.1-dev',
    description = 'A lightweight server to handle Git LFS on different storage backends.',
    long_description = readme,
    license = 'MIT',
    url='git@github.com:gstracquadanio/timone.git',
    keywords='',

    # author information
    author = 'Giovanni Stracquadanio',
    author_email = 'dr.stracquadanio@gmail.com',

    # installation info and requirements
    install_requires=[],
    setup_requires=[],

    # test info and requirements
    test_suite='tests',
    tests_require=[],

    # package deployment info
    include_package_data=True,
    zip_safe=False,

    # all tools have cli interface
    entry_points={
        'console_scripts': [
            'timone=timone.cli:main',
        ],
    },
)
