# Restriccion-SCL-API
[![Build Status](https://travis-ci.org/m4droid/Restriccion-SCL-API.svg?branch=master)](https://travis-ci.org/m4droid/Restriccion-SCL-API)
[![Coverage Status](https://coveralls.io/repos/m4droid/Restriccion-SCL-API/badge.svg?branch=master)](https://coveralls.io/r/m4droid/Restriccion-SCL-API?branch=master)
[![Code Health](https://landscape.io/github/m4droid/Restriccion-SCL-API/master/landscape.svg?style=flat)](https://landscape.io/github/m4droid/Restriccion-SCL-API/master)

Page available at http://restriccion-scl.m4droid.com/

## Resources available
* http://restriccion-scl.m4droid.com/api/0/restricciones

### API develop instructions

##### INSTALL DATABASE
    # OS X
    brew install mongodb

##### INSTALL REQUIRED PACKAGES TO RUN THE TESTS
    pip install nose
    pip install mock
    pip install coverage

##### INSTALL BY HAND
    pip install git+https://github.com/wonderpush/python3-gcm.git
    python setup.py develop

##### CONFIGURE
    # To run tests
    vim configs/tests.json
    
    cp configs/localhost.json{.default,}
    vim configs/localhost.json

##### RUN TESTS
    ./runtests.sh

##### RUN LOCAL WEB SERVICE
    python scripts/serve.py

### HTML develop instructions

##### INSTALL AND GET BOWER DEPENDENCIES
    # Install instructions at http://bower.io/
    
    cd html/
    bower install

##### Run local Python 3 HTTP server
    python -m http.server

## License
MIT