#!/bin/bash -x

docker exec -it signoz-clickhouse clickhouse-client "$@"
