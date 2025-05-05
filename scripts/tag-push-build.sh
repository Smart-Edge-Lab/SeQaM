#!/bin/bash -x

VERSION=$1
git tag -d $VERSION
git tag $VERSION || exit "$?"
git push --force --atomic origin HEAD $VERSION || exit "$?"

cd "$(dirname "$0")"

../api/bin/publish.sh || exit $?
