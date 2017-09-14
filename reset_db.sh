#!/usr/bin/env bash
set -e

dropdb --if-exists xchat_dev
createdb xchat_dev -O xchat
psql xchat_dev < db/xchat_msg.sql

./cmd.sh migrate
./cmd.sh createsuperuser --username xchat --email webee.yw@qq.com
