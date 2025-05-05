#!/bin/bash

echo -e "\U231B Applying configuration"

cd "$(dirname "$0")"

cd ../../../api/bin/
./install.sh
. config.sh
cd -

echo -e "\U2705 Configuration done!"

echo -e "\U231B Deploying an ssh agent $VERSION"

curl "http://${API_HOST}:${API_PORT}/static/ecdsa.pub" || {
  err=$?
  echo "API is unreachable"
  exit $err
}

docker compose up
