# Domain Ops

WLST script for Weblogic domain operations such as checking server status, getting thread dumps, and starting/stopping servers. 
The script can be run in a non-interactive mode to get status and thread dumps for all servers in the domain, or in an interactive mode where the user can execute commands to check status, get thread dumps, and start/stop servers on demand.


## Usage

Show status for all servers in the domain.
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1
```

Show status for all servers in the domain and get thread dumps for each server. If 'write_thread_dump_to_file' parameter is set to *true* in config/config.properties, thread dumps for each server will be written to the location set by 'output_files_path' parameter.
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --get_thread_dumps
```

To start interactive mode:
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --interactive
```

## How to start, using shell script

1) Edit run.sh script and set your target wlst.sh location, weblogic username and admin URL
2) Execute and provide theuser password:

```
./run.sh
```

## Interactive Mode

You will be prompted for operation commands. The options are:

**quit** Exit interactive mode\
Usage: quit\
Synonyms: exit, q, x

**list**: Lists all servers in the domain\
Usage: list\
Synonyms: ls

**status**: Shows status for a list of servers. If no server is specified, show status for all servers\
Usage: status (nothing) or [server number | server name] ... [server number | server name]\
Synonyms: stat

**tdump**: Shows thread dump for a list of servers. If no server is specified, show thread dump for all servers\
Usage: tdump (nothing) or [server number | server name] ... [server number | server name]\
Synonyms: td

**help**: Shows this help message\
Usage: help\
Synonyms: h, ?

**start**: Starts a server or a list of servers\
Usage: start (all |  [server number | server name] ... [server number | server name] )\

**stop**: Stops a server or a list of servers\
Usage: stop (all | [server number | server name] ... [server number | server name] )\

**set**: Shows or sets session variables. To show all session variables, run "set". To show a specific session variable, run "set [variable name]". To set a session variable, run "set [variable name] [new value]"\
Usage: set (nothing) or [variable name] or [variable name] [value]

**reset**: Resets session variables to default values from config file\
Usage: reset

**.**: Repeat latest command\
Usage: .

## Session Variables

Session variables controls application behaviour and are loaded from the config/config.properties file. All variables can be overriden during the interactive session, except for those starting with a "_".

**__admin_server_name** Admin Server name. Used to skip Admin Server from start/stop operations.
**output_files_path** Output files path
**write_thread_dump_to_file** When *true*, thread dumps will be written to the output files path. Otherwise, output goes to stdout.
**cluster_name** When *all*, all servers are displayed or started/stopped, regardless the cluster they belong to. Specify a cluster name, and all operations will affect only servers in that cluster.
**debug_mode** When *true*, show tracebaks in case of error. Otherwise, no tracebacks are displayed.


