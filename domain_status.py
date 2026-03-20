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

def show_server_status(server_name):
    server_runtime = get_server_runtime_by_name(server_name)
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
        print "*** No runtime information found for server: " + server_name
        return None

        
def show_server_thread_dump(server_name):
    server_runtime = get_server_runtime_by_name(server_name)
    if server_runtime is not None:
        jvmRT = server_runtime.getJVMRuntime()
        print("\n\n==========  BEGIN Thread Dump for server " + server_runtime.getName() + " ==========\n")
        print(jvmRT.getThreadStackDump())
        print("\n\n==========  END Thread Dump for server " + server_runtime.getName() + " ==========\n")
    else:
        print "*** No runtime information found for server: " + server_name
        return None

def show_server_list_status(server_name_list):

    for server in server_name_list:
        show_server_status(server['name'])

def show_server_list_thread_dump(server_name_list):

    for server in server_name_list:
        show_server_thread_dump(server['name'])

def get_server_list():
    cd('')
    servers = cmo.getServers()
    server_list = []
    for server in servers:
        server_list.append({
            'name': server.getName(),
            'listen_port': server.getListenPort(),
            'listen_port_ssl': server.getSSL().getListenPort() if server.getSSL() is not None else None,
            'cluster': server.getCluster().getName() if server.getCluster() is not None else None,
            'machine': server.getMachine().getName() if server.getMachine() is not None else None
        })
    # order server_list by cluster, machine, server name and port ans assign a sequential number to each server in the list
    server_list = sorted(server_list, key=lambda x: (x['cluster'] or '', x['machine'] or '', x['name'], x['listen_port'] or 0))
    for i, server in enumerate(server_list):
        server['number'] = i + 1

    return server_list

def show_server_list():
    server_list = get_server_list()
    print("\nServer List:")
    # Print server list in a tabular format
    print("{:<5} {:<20} {:<10} {:<10} {:<20} {:<20}".format("No.", "Name", "Port", "SSL Port", "Cluster", "Machine"))
    print("-" * 85)
    for server in server_list:
        print("{:<5} {:<20} {:<10} {:<10} {:<20} {:<20}".format(
            server['number'],
            server['name'],
            server['listen_port'] if server['listen_port'] is not None else 'N/A',
            server['listen_port_ssl'] if server['listen_port_ssl'] is not None else 'N/A',
            server['cluster'] if server['cluster'] is not None else 'N/A',
            server['machine'] if server['machine'] is not None else 'N/A'
        ))
        state(server['name'],'Server')
    print("-" * 85)
    print("\n")

def show_all_server_list_status():
    all_servers_list = get_server_list()
    for server in all_servers_list:
        show_server_status(server['name'])

def create_command_executor():

    return commands.CommandExecutor(
        commands=[
            commands.Command(name='quit', description='Exit interactive mode', method=None, is_quit_command=True),
            commands.Command(name='list', description='List all servers in the domain', method=globals().get('show_server_list'))
        ]
    )

def interactive_loop():

    command_executor = create_command_executor()

    while True:
        user_input = raw_input(":: ")
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