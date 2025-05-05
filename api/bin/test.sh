#!/bin/bash -x

cd "$(dirname "$0")" || exit $?

. venv.sh

./bin/mypy.sh || exit $?

pwd

pytest
