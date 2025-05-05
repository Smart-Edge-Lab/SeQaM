#!/bin/bash

cd "$(dirname "$0")" || exit $?

pip install --upgrade pip
pip install --upgrade build
python3 -m build || exit $?

cd - || exit $?
