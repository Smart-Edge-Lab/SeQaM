#!/bin/bash -x

cd "$(dirname "$0")"

. venv.sh

pwd

python3 -m mypy --exclude locust-scripts .
