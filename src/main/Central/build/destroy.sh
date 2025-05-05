#!/bin/bash

echo -e "\U231B Tearing down the Central Components of the Cluster Edge Service Quality Manager"

cd "$(dirname "$0")"

cd ../../../../api/bin/
. config.sh
cd -

docker compose down -v

echo -e "\U2705 Modules stopped and removed!"
