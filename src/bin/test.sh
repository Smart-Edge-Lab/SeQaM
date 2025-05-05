#!/bin/bash -x

cd "$(dirname "$0")"

. venv.sh

cd ../..

./bin/mypy.sh || exit $?

pwd

pytest
