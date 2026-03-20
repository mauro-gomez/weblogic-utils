#!/bin/sh

# get password from user
echo "Enter the password for weblogic user: "
read -s PASSWD

/home/opc/java/Oracle_Home14/oracle_common/common/bin/wlst.sh domain_status.py --admin_url t3://localhost:7001 --username weblogic --password $PASSWD --get_thread_dumps --interactive