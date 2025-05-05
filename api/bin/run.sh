#!/bin/bash -x

cd "$(dirname "$0")"

./install.sh
. config.sh

cd ..

. .venv/bin/activate

pip install -r requirements.txt
pip install --force-reinstall ../common/dist/seqam_data_fh_dortmund_project_emulate-0.0.1-py3-none-any.whl

cd src/edpapi_fh_dortmund_project_emulate

export API_HOST="localhost"

fastapi dev --port ${API_PORT}
