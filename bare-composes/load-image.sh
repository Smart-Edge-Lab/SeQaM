#!/bin/sh

gunzip -c "$1" | docker load
