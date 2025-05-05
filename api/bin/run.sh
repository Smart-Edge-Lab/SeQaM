#!/bin/bash -x

cd "$(dirname "$0")"

./install.sh
. config.sh

cd ..

. .venv/bin/activate

pip install -r requirements.txt

cd src/edpapi_fh_dortmund_project_emulate

export API_HOST="localhost"

fastapi dev --port ${API_PORT}
