# Restriccion-API
[![Build Status](https://travis-ci.org/m4droid/Restriccion-API.svg?branch=master)](https://travis-ci.org/m4droid/Restriccion-API)
[![Coverage Status](https://coveralls.io/repos/m4droid/Restriccion-API/badge.svg?branch=master)](https://coveralls.io/r/m4droid/Restriccion-API?branch=master)
[![Code Health](https://landscape.io/github/m4droid/Restriccion-API/master/landscape.svg?style=flat)](https://landscape.io/github/m4droid/Restriccion-API/master)

Page available at http://restriccion.m4droid.com/

## Resources available
* http://restriccion.m4droid.com/api/0/restricciones

### API develop instructions

##### INSTALL DATABASE
    # OS X
    brew install mongodb

##### INSTALL REQUIREMENTS
    python setup.py develop

##### INSTALL TEST REQUIREMENTS
    pip install coverage

##### CONFIGURE
    # To run tests
    vim configs/tests.json
    
    cp configs/localhost.json{.default,}
    vim configs/localhost.json

##### RUN LOCAL WEB SERVICE
    python scripts/serve.py

##### RUN TESTS
    ./runtests.sh

## License
MIT
