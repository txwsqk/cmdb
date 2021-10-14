#!/bin/bash
source /root/.pyenv/versions/cmdb/bin/activate
source /etc/environment
cd /data1/cmdb-api
python get_ecs_from_api.py
python cmdb/utils/bill.py
