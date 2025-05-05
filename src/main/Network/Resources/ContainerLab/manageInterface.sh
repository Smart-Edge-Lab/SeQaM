#!/bin/sh

nrate=$(($1*1024))
echo "nwe rate is $nrate "
containerlab tools netem set -n clab-testnetwork-router1 -i eth2 --rate  $nrate
sleep $2

containerlab tools netem set -n clab-testnetwork-router1 -i eth2
