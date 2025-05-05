#!/bin/bash

echo -e "\U231B Applying configuration"

cd "$(dirname "$0")"

cd ../../../../../api/bin/
./install.sh
. config.sh
cd -

echo -e "\U2705 Configuration done!"

echo -e "\U231B Deploying the Network Event Manager $VERSION of the Cluster Edge Service Quality Manager"

docker compose up
