#!/bin/bash

echo -e "\U231B Applying configuration"

cd "$(dirname "$0")"

cd ../../../../../api/bin/
. config.sh
cd -

echo -e "\U2705 Configuration done!"

echo -e "\U231B Stopping the Distributed Component of the Cluster Edge Service Quality Manager"

docker compose -f ./docker-compose.yml down
