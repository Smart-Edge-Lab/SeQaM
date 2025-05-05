#!/bin/bash -x

cd "$(dirname "$0")"

./build.sh || exit $?

. config.sh

./push-docker-images.sh || exit $?

git remote remove private-git
git remote add private-git "$PRIVATE_GIT_REPOSITORY"
git checkout dev
git merge origin/dev
git push --no-verify --tags --force private-git HEAD
