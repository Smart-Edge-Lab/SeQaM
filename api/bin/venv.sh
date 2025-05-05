#!/bin/bash -x

cd "$(dirname "$0")" || exit $?

cd ..

python -m venv .venv || exit $?

. .venv/bin/activate

pip install -r requirements.txt || exit $?
pip install -r requirements-test.txt || exit $?

../common/build.sh || exit $?
pip install --force-reinstall ../common/dist/*.whl || exit $?
