#!/usr/bin/env bash
set -e
set -x

p=${1:-dev}
u=${2:-$(whoami)}
db_name=xchat_${p}

sudo -u ${u} dropdb --if-exists ${db_name}
sudo -u ${u} createdb ${db_name} -O xchat_dev
sudo -u ${u} psql ${db_name} < <(sed -e 's/OWNER TO xchat/OWNER TO xchat_dev/' db/xchat_msg.sql)

./cmd.sh -e ${p} migrate
./cmd.sh -e ${p} createsuperuser --username xchat --email webee.yw@qq.com
