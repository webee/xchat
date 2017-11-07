#!/usr/bin/env bash
set -e

db_name=xchat_${1:-dev}

dropdb --if-exists ${db_name}
createdb ${db_name} -O xchat_dev
psql ${db_name} < db/xchat_msg.sql

./cmd.sh migrate
./cmd.sh createsuperuser --username xchat --email webee.yw@qq.com
