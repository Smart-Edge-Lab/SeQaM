#!/bin/bash -x

cd "$(dirname "$0")"

./install.sh
. config.sh

docker run --rm --name edpapi -e DATABASE_ENDPOINT="$DATABASE_ENDPOINT" -p ${API_PORT}:80 "$EDPAPI_IMAGE_NAME"
