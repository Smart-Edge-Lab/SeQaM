#!/bin/bash -x

cd "$(dirname "$0")"

. venv.sh

./bin/mypy.sh || exit $?

pwd

pytest
