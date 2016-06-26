#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

RESTRICCION_CONFIG="$DIR/configs/tests.json" coverage run --source=restriccion_scl setup.py test
