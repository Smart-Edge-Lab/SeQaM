#!/bin/sh
speed=$1
time_in_seconds=$2
router_name=$3
interface=$4

nrate=$(($speed * 1024))
echo "nwe rate is $nrate "
containerlab tools netem set -n clab-testnetwork-$router_name -i $interface --rate $nrate
sleep $time_in_seconds
containerlab tools netem set -n clab-testnetwork-$router_name -i $interface