#!/bin/bash

echo -e "\U231B Applying configuration"

cd "$(dirname "$0")"

cd ../../../../api/bin/
./install.sh

. config.sh

. check-health.sh
cd -

echo -e "\U2705 Configuration done!"

echo -e "\U231B Deploying the Central Components $VERSION of the Cluster Edge Service Quality Manager"
echo -e "\U26A0 If you get an error with the ports, make sure you have configured the environmental variables first"

docker compose -f ./docker-compose.yaml up -d --remove-orphans || exit $?
sleep 2
check_central_components_health

echo -e "\U2705 Modules up and running!"

echo -e "\U231B Open the console navigating your web browser to http://${API_HOST}:${API_PORT}"
