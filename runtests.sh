#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export RESTRICCION_SCL_CONFIG="$DIR/configs/tests.json"

nosetests --with-coverage --cover-package=restriccion_scl "$@"
