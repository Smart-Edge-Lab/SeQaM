#!/bin/bash

cd "$(dirname "$0")"

cd ../../../../../api/bin/ || {
  err=$?
  pwd
  exit $err
}
pip install --force-reinstall ../../common/dist/seqam_data_fh_dortmund_project_emulate-0.0.1-py3-none-any.whl
./install.sh
. config.sh
cd -

python3 DistEventManagerModule.py
