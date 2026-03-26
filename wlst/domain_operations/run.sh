#!/bin/sh

# get password from user
echo "Enter the password for weblogic user: "
read -s PASSWD
# 12.2.1.4
#/home/opc/java/Oracle_Home12214/oracle_common/common/bin/wlst.sh domain_ops_12.py --admin_url t3://localhost:7001 --username weblogic --password $PASSWD --get_thread_dumps --interactive
# 14.1.1
#/home/opc/java/Oracle_Home14/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password $PASSWD --get_thread_dumps --interactive
# 14.1.2
#/home/opc/java/Oracle_Home1412/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password $PASSWD --get_thread_dumps --interactive
# 15.1.1
#/home/opc/java/Oracle_Home1511/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password $PASSWD --get_thread_dumps --interactive
# 14.1.1 Quick
/home/opc/java/Oracle_Home1411_Quick/wls1411/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password $PASSWD --get_thread_dumps --interactive
