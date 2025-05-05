#!/bin/bash -x

#git checkout dev || exit $?
#git pull --no-rebase origin dev || exit $?

cd "$(dirname "$0")"

cd ..

VERSION="$(git describe --tags)"

ARCHIVE="/tmp/seqam-${VERSION}.tgz"

tar --exclude='*.jpg' --exclude='.git' --exclude='.idea' --exclude='__pycache__' --exclude='.venv' \
  --exclude='.pytest_cache' \
  --exclude='venv' \
  --exclude='.mypy_cache' --exclude='./src/main/Central/Collector' \
  --exclude='./src/main/Distributed/Collector' \
  --exclude='scenario_*.txt' \
  --exclude='./src/main/Test/yolo-app/server/weights/End-to-end.pth' \
  --exclude='./src/main/Central/Modules/DataManager/img/*' \
  --exclude='*.mkv' \
  --exclude='*.mp4' \
  --exclude='*.jpg' \
  --exclude='*.png' \
  --exclude='./bare-composes/seqam-*/*' \
  -czvf "$ARCHIVE" .

echo "$ARCHIVE $(du -h $ARCHIVE) is released. You can send it to your storage for backup and use"
