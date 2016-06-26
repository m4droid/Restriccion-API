from setuptools import setup, find_packages


version = '0.0.1'

setup(
    name='restriccion',
    version=version,
    description="Restriccion API",
    long_description="""""",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Francisco Madrid',
    author_email='fjmadrid@gmail.com',
    url='https://github.com/m4droid/Restriccion-API',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask==0.11.1',
        'flask-cors==2.1.2',
        'pymongo==3.2.2',
        'pyquery==1.2.13',
        'moment==0.5.1',
        'validate_email==1.3',
        'python-gcm==0.4',
    ],
    tests_require=[
        'nose',
        'mock',
        'coverage',
    ],
    test_suite="tests",
    entry_points={},
)
