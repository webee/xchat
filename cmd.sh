#!/usr/bin/env bash

cd $(dirname $0)
if [ "$1" = "-e" ]; then
    env=${2:-dev}
    shift 2
    export ENV=${env}
fi

source ./venv/bin/activate

./src/manage.py "$@"
