#!/bin/bash -x

JENKINS_URL=http://172.22.174.190:8080
AUTH=pigovsky:1165b24f0e4e160ccbd6eeedeae276c2d3

curl -X POST -L --user $AUTH $JENKINS_URL/job/EDPAPI/build?token=EMULATE
