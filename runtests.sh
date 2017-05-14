#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
COVERAGE_DIR="$DIR/coverage"

ENV=test nosetests --with-coverage --cover-package=restriccion --cover-html --cover-html-dir=$COVERAGE_DIR $@
