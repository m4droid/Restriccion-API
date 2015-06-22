# Restriccion-SCL-API
[![Build Status](https://travis-ci.org/m4droid/Restriccion-SCL-API.svg?branch=master)](https://travis-ci.org/m4droid/Restriccion-SCL-API)
[![Coverage Status](https://coveralls.io/repos/m4droid/Restriccion-SCL-API/badge.svg?branch=master)](https://coveralls.io/r/m4droid/Restriccion-SCL-API?branch=master)
[![Code Health](https://landscape.io/github/m4droid/Restriccion-SCL-API/master/landscape.svg?style=flat)](https://landscape.io/github/m4droid/Restriccion-SCL-API/master)

#### INSTALL PACKAGES TO RUN THE TESTS
    pip install nose
    pip install mock
    pip install coverage

#### INSTALL BY HAND
    pip install git+https://github.com/wonderpush/python3-gcm.git

#### CONFIGURE
    vim configs/tests.json

    cp configs/localhost.json{.default,}
    vim configs/localhost.json

#### RUN WEB SERVICE
    python scripts/serve.py
