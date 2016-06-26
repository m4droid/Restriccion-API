#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export RESTRICCION_CONFIG="$DIR/configs/tests.json"

coverage run --source=restriccion setup.py test
