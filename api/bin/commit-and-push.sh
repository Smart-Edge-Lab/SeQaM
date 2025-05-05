#!/bin/bash -x

git commit -a
VERSION=$1
git tag $VERSION
git push --atomic origin HEAD $VERSION

cd "$(dirname "$0")"

./build.sh
