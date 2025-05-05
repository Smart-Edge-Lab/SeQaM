#!/bin/bash -x

cd "$(dirname "$0")"

. venv.sh

python3 -m mypy --strict src/ tests/
