#!/bin/bash -x

cd "$(dirname "$0")"

cd ../main/Central

python -m venv .venv || exit $?

. .venv/bin/activate

pip install -r build/requirements.txt
pip install -r ../../../api/requirements-test.txt
