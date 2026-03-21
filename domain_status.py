#
# WLST
#
# This script is used to check the status of a WebLogic domain.
# It connects to the Admin Server and retrieves the status of all servers in the domain.
# Usage:
#   java weblogic.WLST domain_status.py <admin_url> <username> <password> <get
# Import necessary modules
import sys
from weblogic.management.scripting.utils import WLSTUtil
import argparse
import commands
import servers

def get_server_runtimes():
    # only returns the currently running servers in the domain
    domainRuntime()
    return domainRuntimeService.getServerRuntimes()

def get_server_runtime_by_name(server_name):
    serverRuntimes = get_server_runtimes()
    for serverRuntime in serverRuntimes:
        if serverRuntime.getName() == server_name:
            return serverRuntime
    return None

def get_server_by_identifier(server_identifier):
    server_list = get_server_list()
    for server in server_list:
        if str(server.number) == server_identifier or server.getName() == server_identifier:
            return server
    return None

def get_server_list_from_identifiers(server_identifiers):
    output_server_list = []

    for identifier in server_identifiers:
        server = get_server_by_identifier(identifier)
        if server is not None:
            output_server_list.append(server)
        else:
            raise ValueError("No server found with identifier: " + identifier)

    return output_server_list

def show_server_status(server):
    server_runtime = get_server_runtime_by_name(server.getName())
    if server_runtime is not None:
        print "\n" + server_runtime.getName() + " " + server_runtime.getState()
        jvmRT = server_runtime.getJVMRuntime()

        print("\n  -- Memory --")
        print("  HeapFreeCurrent " + str(jvmRT.getHeapFreeCurrent()))
        print("  HeapFreePercent " + str(jvmRT.getHeapFreePercent()))
        print("  HeapSizeCurrent " + str(jvmRT.getHeapSizeCurrent()))
        print("  HeapSizeMax     " + str(jvmRT.getHeapSizeMax()))

        threadPoolRT = server_runtime.getThreadPoolRuntime()
        print("\n  -- Threads --")
        print("  ExecuteThreadTotalCount " + str(threadPoolRT.getExecuteThreadTotalCount()))
        print("  ExecuteThreadIdleCount  " + str(threadPoolRT.getExecuteThreadIdleCount()))
        print("  Throughput              " + str(threadPoolRT.getThroughput()))
        print("  HoggingThreadCount      " + str(threadPoolRT.getHoggingThreadCount()))
        print("  StuckThreadCount        " + str(threadPoolRT.getStuckThreadCount()))
        print("  CompletedRequestCount   " + str(threadPoolRT.getCompletedRequestCount()))
        print("  QueueLength             " + str(threadPoolRT.getQueueLength()))
        print("")
        for thread in threadPoolRT.getExecuteThreads():
            print "  Thread '" + thread.getName() + "' - Hogger: " + str(thread.isHogger()) + " - Current Request: " + str(thread.getCurrentRequest())

        jdbcServiceRT = server_runtime.getJDBCServiceRuntime()
        dataSources = jdbcServiceRT.getJDBCDataSourceRuntimeMBeans()
        if (len(dataSources) > 0):
            print('\n  -- Datasources --')
            for dataSource in dataSources:
                testPool = dataSource.testPool()
                dataSourceName = dataSource.getName()
                if (testPool == None):
                    print '\n    ' + dataSourceName+'\t'+dataSource.getState()+'\tOK\n'
                    print("      CurrCapacity                  " + str(dataSource.getCurrCapacity()))
                    print("      ConnectionsTotalCount         " + str(dataSource.getConnectionsTotalCount()))
                    print("      ConnectionDelayTime           " + str(dataSource.getConnectionDelayTime()))
                    print("      ActiveConnectionsAverageCount " + str(dataSource.getActiveConnectionsAverageCount()))
                    print("      ActiveConnectionsCurrentCount " + str(dataSource.getActiveConnectionsCurrentCount()))
                    print("      ActiveConnectionsHighCount    " + str(dataSource.getActiveConnectionsHighCount()))
                    print("      FailuresToReconnectCount      " + str(dataSource.getFailuresToReconnectCount()))
                    print("      LeakedConnectionCount         " + str(dataSource.getLeakedConnectionCount()))
                else:
                    print '\n    ' + dataSourceName+'\t'+dataSource.getState()+'\tFailure: '
                    print testPool

    else:
        print "*** No runtime information found for server: " + server.getName()
        return None

        
def show_server_thread_dump(server):
    server_runtime = get_server_runtime_by_name(server.getName())
    if server_runtime is not None:
        jvmRT = server_runtime.getJVMRuntime()
        print("\n\n==========  BEGIN Thread Dump for server " + server_runtime.getName() + " ==========\n")
        print(jvmRT.getThreadStackDump())
        print("\n\n==========  END Thread Dump for server " + server_runtime.getName() + " ==========\n")
    else:
        print "*** No runtime information found for server: " + server.getName()
        return None

def show_server_list_status(server_list = []):

    if len(server_list) == 0:
        server_list = get_server_list()

    for server in server_list:
        show_server_status(server)

def show_server_list_thread_dump(server_list = []):

    if len(server_list) == 0:
        server_list = get_server_list()

    for server in server_list:
        show_server_thread_dump(server)

def get_server_list():

    domainConfig()
    cd('/')
    tree_servers = cmo.getServers()
    server_list = []
    for tree_server in tree_servers:

        server = servers.Server(
            name=tree_server.getName(),
            listen_port=tree_server.getListenPort(),
            listen_port_ssl=tree_server.getSSL().getListenPort() if tree_server.getSSL() is not None else None,
            cluster=tree_server.getCluster().getName() if tree_server.getCluster() is not None else None,
            machine=tree_server.getMachine().getName() if tree_server.getMachine() is not None else None
        )
        server_list.append(server)
    # order server_list by cluster, machine, server name and port ans assign a sequential number to each server in the list
    server_list = sorted(server_list, key=lambda x: (x.getCluster() or '', x.getMachine() or '', x.getName(), x.getListenPort() or 0))
    for i, server in enumerate(server_list):
        server.number = i + 1

    return server_list

def show_server_list():
    server_list = get_server_list()
    print("\nServer List:")
    # Print server list in a tabular format
    print("{:<5} {:<20} {:<10} {:<10} {:<20} {:<20}".format("No.", "Name", "Port", "SSL Port", "Cluster", "Machine"))
    print("-" * 85)
    for server in server_list:
        print("{:<5} {:<20} {:<10} {:<10} {:<20} {:<20}".format(
            server.number,
            server.getName(),
            server.getListenPort() if server.getListenPort() is not None else 'N/A',
            server.getListenPortSSL() if server.getListenPortSSL() is not None else 'N/A',
            server.getCluster() if server.getCluster() is not None else 'N/A',
            server.getMachine() if server.getMachine() is not None else 'N/A'
        ))
        state(server.getName(),'Server')
    print("-" * 85)
    print("\n")

def show_all_server_list_status():
    all_servers_list = get_server_list()
    for server in all_servers_list:
        show_server_status(server)

def start_server(server):
    print "Starting server: " + server.getName()
    start(server.getName(), 'Server', block='false')

def start_server_list(server_list):
    for server in server_list:
        start_server(server)

def stop_server(server):
    print "Stopping server: " + server.getName()
    shutdown(server.getName(), 'Server', force='true', block='false')

def stop_server_list(server_list):
    for server in server_list:
        stop_server(server)

def create_command_executor():

    return commands.CommandExecutor(
        commands=[
            commands.Command(name='quit', description='Exit interactive mode', synonyms=['exit', 'q', 'x'], is_quit_command=True),
            commands.Command(name='list', description='Lists all servers in the domain', synonyms=['ls'], method=globals().get('show_server_list')),
            commands.Command(name='status', description='Shows status for a list of servers. If no server is specified, show status for all servers', params_description='(nothing) or [server number | server name] ... [server number | server name]', synonyms=['stat'], method=globals().get('show_server_list_status'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='tdump', description='Shows thread dump for a list of servers. If no server is specified, show thread dump for all servers', params_description='(nothing) or [server number | server name] ... [server number | server name]', synonyms=['td'], method=globals().get('show_server_list_thread_dump'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='help', description='Shows this help message', synonyms=['h', '?'], is_help_command=True),
            commands.Command(name='start', description='Starts a server or a list of servers', params_description='[server number | server name] ... [server number | server name]', method=globals().get('start_server_list'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='stop', description='Stops a server or a list of servers', params_description='[server number | server name] ... [server number | server name]', method=globals().get('stop_server_list'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers'))
        ]
    )

def interactive_loop():

    command_executor = create_command_executor()

    while True:
        user_input = raw_input(":: ")
        if user_input.strip() == "":
            continue

        command_result = command_executor.execute_command(user_input)
        if command_result is not None:
            if command_result.get_is_quit_command():
                print "Exiting interactive mode."
                break
            elif command_result.get_success():
                if command_result.get_data() is not None:
                    print command_result.get_data()
            else:
                print "Command execution failed. Message:"
                print command_result.get_message()
            print "\n"

def process(username, password, admin_url, get_thread_dumps=False, interactive_mode=False):
    
    connect(username, password, admin_url)

    show_server_list()

    if interactive_mode:
        interactive_loop()
    else:
        show_all_server_list_status()
        if get_thread_dumps:
            show_all_server_list_thread_dump()

    disconnect()

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Check WebLogic domain status.')
    parser.add_argument('--admin_url', help='Admin server URL')
    parser.add_argument('--username', help='Admin username')
    parser.add_argument('--password', help='Admin password')
    parser.add_argument('--get_thread_dumps', action='store_true', help='Whether to get thread dumps for each server')
    parser.add_argument('--interactive', '-i', action='store_true', help='Enable interactive mode')
    args = parser.parse_args()

    admin_url = args.admin_url
    username = args.username
    password = args.password
    get_thread_dumps = args.get_thread_dumps
    interactive_mode = args.interactive

    process(username, password, admin_url, get_thread_dumps, interactive_mode)