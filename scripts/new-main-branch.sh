#!/bin/bash -x

git fetch origin
git checkout -b $1 origin/main
