#!/bin/sh
cd loadclient
   docker build -t loadclient .
cd ../loadserver
   docker build -t loadserver .
cd ../mclient
   docker build -t mclient .
cd ../mserver
   docker build -t mserver .
