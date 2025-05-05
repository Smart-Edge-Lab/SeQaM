#!/bin/bash

cd "$(dirname "$0")" || exit $?

tags="$(git for-each-ref --sort=creatordate --format '%(refname)' refs/tags)"

for current_tag in $tags
do
  if [ -n "$prev_tag" ]
  then
    echo $current_tag
    git log --pretty=oneline $prev_tag..$current_tag
    echo
  fi
  prev_tag=$current_tag
done

