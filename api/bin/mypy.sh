#!/bin/bash -x

cd "$(dirname "$0")" || exit $?

cd ..

. .venv/bin/activate

python3 -m mypy --strict src/ tests/
