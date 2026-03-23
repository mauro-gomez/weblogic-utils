# Domain Ops

WLST script for Weblogic domain operations such as checking server status, getting thread dumps, and starting/stopping servers. 
The script can be run in a non-interactive mode to get status and thread dumps for all servers in the domain, or in an interactive mode where the user can execute commands to check status, get thread dumps, and start/stop servers on demand.


## Usage

To check status for all servers in the domain and get thread dumps for each server:
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --get_thread_dumps
```

To check status for all servers in the domain without getting thread dumps:
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1
```

To start interactive mode:
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --interactive
```
