# Domain Ops

WLST script for Weblogic domain operations such as checking server status, getting thread dumps, and starting/stopping servers. 
The script can be run in a non-interactive mode to get status and thread dumps for all servers in the domain, or in an interactive mode where the user can execute commands to check status, get thread dumps, and start/stop servers on demand.

Domain Ops script needs a Weblogic user in *Monitors* security group for almost all commands. Fot start/stop commands, the user must belong at least to *Operators* group. 

Domain configuration changes are out of the scope of this script.


## Usage

Show status for all servers in the domain.
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1
```

Show status for all servers in the domain and get one single thread dump for each server. If 'write_thread_dump_to_file' parameter is set to *true* in config/config.properties, thread dumps will be written to the location set by 'output_files_path' parameter.
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --get_thread_dumps
```

To start interactive mode:
```
   $FMW_HOME/oracle_common/common/bin/wlst.sh domain_ops.py --admin_url t3://localhost:7001 --username weblogic --password welcome1 --interactive
```


## How to start, using shell script

1) Edit run.sh script and set your target wlst.sh location, weblogic username and admin URL
2) Execute and provide the user password:

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

**tdump**: Shows a single thread dump for a list of servers. If no server is specified, show the thread dump for all servers\
Usage: tdump (nothing) or [server number | server name] ... [server number | server name]\
Synonyms: td

**rtdump**: Shows repeated thread dumps for a list of servers, according to session variables. If no server is specified, show thread dumps for all servers\
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

**output_files_path** Output files path.

**write_thread_dump_to_file** When *true*, thread dumps will be written to the output files path. Otherwise, output goes to stdout.

**cluster_name** When *all*, all servers are displayed or started/stopped, regardless the cluster they belong to. Specify a cluster name, and all operations will affect only servers in that cluster.

**debug_mode** When *true*, show tracebaks in case of error. Otherwise, no tracebacks are displayed.

**repeated_thread_dump_count** For thread dump analysis, how many thread dumps are taken for each server in a single execution.

**repeated_thread_dump_interval_seconds** Seconds to wait between repeated thread dumps.


## Interactive mode examples

### Domain status summary

Show server list and status summary
```
:: list

Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : RUNNING
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : RUNNING
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------
```

When specified in command parameters, all servers can be referenced by its name or number.
```
:: status ManagedServer_1 4 ManagedServer_4
```
is the same as
```
:: status ManagedServer_1 ManagedServer_3 ManagedServer_4
```

### Filter servers by cluster

Here, we set a session-scoped value for the cluster_name parameter. Please note that you don't need to write the entire variable name, but just the first characters which identify the variable name ("set cluster_name (value)" is the same as "set c (calue)"). 

The cluster filter applies the same for all operations. Listing, getting status amd starting/stopping will apply only for the servers included in the cluster filter. If the cluster filter is set to "all" (the default value), all servers are allowed in parameters. In any case, the server identified by Admin Server cannot be started/stopped in the interactive mode.

Finally, we execute "reset" command to switch back to defaults for all sesion variables.


```
:: set
Current session values:
cluster_name = all
debug_mode = false
repeated_thread_dump_interval_seconds = 5
write_thread_dump_to_file = true
output_files_path = output_files/
repeated_thread_dump_count = 3



:: set cluster_name Cluster-B
Current session values:
Set session variable 'cluster_name' to value: Cluster-B



[Cluster-B] :: list

Server List:
filtered by cluster: Cluster-B
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------




[Cluster-B] :: reset
Session values have been reset to default values from config file.
Current session values:
cluster_name = all
debug_mode = false
repeated_thread_dump_interval_seconds = 5
write_thread_dump_to_file = true
output_files_path = output_files/
repeated_thread_dump_count = 3



:: list

Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : RUNNING
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : RUNNING
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------
```

### Stop and start servers

We can stop specific servers, and then use the "all" keyword to send a Start message to all servers.
```
:: list

Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : RUNNING
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : RUNNING
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------




:: stop 2 3
You are about to stop the following servers:
- ManagedServer_1
- ManagedServer_2
Are you sure you want to proceed? (yes/no): yes
Stopping server: ManagedServer_1
Shutting down the server ManagedServer_1 with force=true while connected to AdminServer ...

The server shutdown task for server ManagedServer_1 
is assigned to variable ManagedServer_1Task 
You can call the getStatus(), getError(), getDescription() 
or isRunning() methods on this variable to determine 
the status of your server shutdown

Stopping server: ManagedServer_2
Shutting down the server ManagedServer_2 with force=true while connected to AdminServer ...

The server shutdown task for server ManagedServer_2 
is assigned to variable ManagedServer_2Task 
You can call the getStatus(), getError(), getDescription() 
or isRunning() methods on this variable to determine 
the status of your server shutdown



:: list

Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : SHUTDOWN
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : SHUTDOWN
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------




:: start all
You are about to start the following servers:
- ManagedServer_1
- ManagedServer_2
- ManagedServer_3
- ManagedServer_4
Are you sure you want to proceed? (yes/no): yes
Starting server: ManagedServer_1
Starting server ManagedServer_1 ...
The server start status task for server ManagedServer_1 is assigned to variable ManagedServer_1Task

You can call the getStatus(), getError(), getDescription() or isRunning() 
methods on this variable to determine the status of your server start

Starting server: ManagedServer_2
Starting server ManagedServer_2 ...
The server start status task for server ManagedServer_2 is assigned to variable ManagedServer_2Task

You can call the getStatus(), getError(), getDescription() or isRunning() 
methods on this variable to determine the status of your server start

Starting server: ManagedServer_3
Starting server ManagedServer_3 ...
The server start status task for server ManagedServer_3 is assigned to variable ManagedServer_3Task

You can call the getStatus(), getError(), getDescription() or isRunning() 
methods on this variable to determine the status of your server start

Starting server: ManagedServer_4
Starting server ManagedServer_4 ...
The server start status task for server ManagedServer_4 is assigned to variable ManagedServer_4Task

You can call the getStatus(), getError(), getDescription() or isRunning() 
methods on this variable to determine the status of your server start



:: list

Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : STARTING
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : STARTING
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------




:: list

Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : RUNNING
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : RUNNING
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------
```

### Get a single thread dump

Here we are getting a single thread dump for a specific server.

```
:: list

Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : RUNNING
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : RUNNING
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------




:: td 4
Location changed to domainRuntime tree. This is a read-only tree 
with DomainMBean as the root MBean. 
For more help, use help('domainRuntime')

Collecting thread dump 1 of 1 for server 'ManagedServer_3'...
Thread dumps for server 'ManagedServer_3' had been written to file: output_files/thread_dump_ManagedServer_3_20260324_130810.txt
```

### Get a sequence of thread dumps

Here we get a sequence of thread dumps for two servers.

```
:: list


Server List:
No.   Name                 Port       SSL Port   Cluster              Machine             
-------------------------------------------------------------------------------------
1     AdminServer          7001       7002       N/A                  N/A                 
Current state of "AdminServer" : RUNNING
2     ManagedServer_1      7003       7004       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_1" : RUNNING
3     ManagedServer_2      7005       7006       Cluster-A            UnixMachine_1       
Current state of "ManagedServer_2" : RUNNING
4     ManagedServer_3      7007       7008       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_3" : RUNNING
5     ManagedServer_4      7009       7010       Cluster-B            UnixMachine_1       
Current state of "ManagedServer_4" : RUNNING
-------------------------------------------------------------------------------------




:: set 
Current session values:
cluster_name = all
debug_mode = false
repeated_thread_dump_interval_seconds = 5
write_thread_dump_to_file = true
output_files_path = output_files/
repeated_thread_dump_count = 3



:: rtd 4 5

Collecting thread dump 1 of 3 for server 'ManagedServer_3'...
Collecting thread dump 2 of 3 for server 'ManagedServer_3'...
Collecting thread dump 3 of 3 for server 'ManagedServer_3'...
Thread dumps for server 'ManagedServer_3' had been written to file: output_files/thread_dump_ManagedServer_3_20260324_131228.txt
Collecting thread dump 1 of 3 for server 'ManagedServer_4'...
Collecting thread dump 2 of 3 for server 'ManagedServer_4'...
Collecting thread dump 3 of 3 for server 'ManagedServer_4'...
Thread dumps for server 'ManagedServer_4' had been written to file: output_files/thread_dump_ManagedServer_4_20260324_131238.txt
```

