#!/bin/sh
load=$1
time_in_seconds=$2
echo "new load from iperf3 is $load for $time_in_seconds seconds"

rate=$1M
echo "data  $rate on $IPERF_SERVER"
iperf3 -c "$IPERF_SERVER" -b$rate -t $time_in_seconds --timestamps --logfile iperfLog.txt
