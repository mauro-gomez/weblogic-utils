# Domain Ops

WLST script for Weblogic domain operations such as checking server status, getting thread dumps, and starting/stopping servers. 
The script can be run in a non-interactive mode to get status and thread dumps for all servers in the domain, or in an interactive mode where the user can execute commands to check status, get thread dumps, and start/stop servers on demand.


Usage:

1) To check status for all servers in the domain and get thread dumps for each server:
```
   java weblogic.WLST domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --get_thread_dumps
```

2) To check status for all servers in the domain without getting thread dumps:
```
   java weblogic.WLST domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1
```

3) To start interactive mode:
```
   java weblogic.WLST domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --interactive
```