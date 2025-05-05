#!/bin/bash

cd "$(dirname "$0")"

cd ../../../../../api/bin/ || {
  err=$?
  pwd
  exit $err
}
./install.sh

. config.sh

cd -

python3 ExperimentDispatcherModule.py --mode trigger
