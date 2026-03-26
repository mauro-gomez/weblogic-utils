#!/bin/sh

# get password from user
echo "Enter the password for weblogic user: "
read -s PASSWD

/u01/app/oracle/middleware/Oracle_Home1411_Lite/wls1411/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password $PASSWD --get_thread_dumps