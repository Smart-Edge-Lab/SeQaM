#!/bin/bash -x

cd "$(dirname "$0")"

cd ..

python -m venv .venv || exit $?

. .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-test.txt
