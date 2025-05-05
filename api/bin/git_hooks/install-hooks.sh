#!/bin/bash -x

cd "$(dirname "$0")"

cd ../../../.git/hooks

ln -sf ../../api/bin/git_hooks/pre-push .
