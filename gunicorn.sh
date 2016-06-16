#!/usr/bin/env bash

env=${1:-dev}
port=${2:-9980}
NUM_WORKERS=${3:-16}

PROJ_ROOT=$(dirname $0)
NAME=$(basename $PROJ_ROOT)
SRC_DIR=${PROJ_ROOT}/src
VENV_DIR=${PROJ_ROOT}/venv

echo "Starting $NAME $env"
source ${VENV_DIR}/bin/activate
export PYTHONPATH=${SRC_DIR}:${PYTHONPATH}
export ENV=${env}

exec gunicorn -c ${PROJ_ROOT}/deploy/gunicorn.conf.py -b 0.0.0.0:${port} \
  --name ${NAME} \
  -k gevent \
  -w ${NUM_WORKERS} \
  --max-requests 10240 \
  --max-requests-jitter 100 \
  --access-logfile ${PROJ_ROOT}/logs/access.log \
  --error-logfile ${PROJ_ROOT}/logs/error.log \
  --log-level warning \
  ${NAME}_site.wsgi
