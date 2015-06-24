from setuptools import setup, find_packages
import sys, os


version = '0.0.1'

setup(
    name='restriccion_scl',
    version=version,
    description="Restriccion SCL API",
    long_description="""""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Francisco Madrid',
    author_email='fjmadrid@gmail.com',
    url='https://github.com/m4droid/Restriccion-SCL-API',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask>=0.10.1',
        'flask-cors>=2.0.1',
        # 'tornado',
        'pymongo>=3.0.2',
        'pyquery>=1.2.9',
        'moment>=0.2.2',
        'validate_email>=1.3',
    ],
    tests_require=['nose', 'mock', 'coverage'],
    test_suite="tests",
    entry_points={},
)
