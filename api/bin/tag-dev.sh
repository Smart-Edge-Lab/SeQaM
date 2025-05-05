#!/bin/bash -x

git fetch origin
VERSION=$1
git tag "$VERSION" origin/dev
git push --no-verify origin "$VERSION"

cd "$(dirname "$0")"
./trigger-jenkins-build.sh
