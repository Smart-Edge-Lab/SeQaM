#!/bin/sh
clab deploy --topo testnetwork.yml
bash interfaces.sh
bash resource-management.sh
