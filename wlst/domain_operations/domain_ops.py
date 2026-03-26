#
# domain_ops.py
#

# Import necessary modules
import sys
from weblogic.management.scripting.utils import WLSTUtil
import argparse
import commands
import servers

config_properties_file_path = "config/config.properties"
config_properties = {}

domain_context = None

def get_properties_from_file(file_path):
    properties = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key_value = line.split('=', 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        properties[key] = value
    except Exception as e:
        print "Error loading properties from file: " + str(e)
    return properties

def load_config_properties():
    global config_properties
    config_properties = get_properties_from_file(config_properties_file_path)

def get_server_runtimes():
    # only returns the currently running servers in the domain
    global domain_context
    if domain_context != "runtime":
        domainRuntime()
        domain_context = "runtime"

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

class NoServerFound(Exception):
    """Exception raised when no server is found with a given identifier."""
    pass

def get_server_list_from_identifiers(server_identifiers):
    output_server_list = []

    if len(server_identifiers) > 0 and server_identifiers[0].lower() == 'all':
        output_server_list = get_server_list()
    else:
        for identifier in server_identifiers:
            server = get_server_by_identifier(identifier)
            if server is not None:
                output_server_list.append(server)
            else:
                raise NoServerFound(identifier)

    return output_server_list

def get_server_status_report(server):

    status_report = "Status for server '" + server.getName() + "':\n"
    server_runtime = get_server_runtime_by_name(server.getName())
    if server_runtime is not None:
        status_report += "\n" + server_runtime.getName() + " " + server_runtime.getState()
        jvmRT = server_runtime.getJVMRuntime()

        status_report += "\n\n  -- Memory --"
        status_report += "\n  HeapFreeCurrent " + str(jvmRT.getHeapFreeCurrent())
        status_report += "\n  HeapFreePercent " + str(jvmRT.getHeapFreePercent())
        status_report += "\n  HeapSizeCurrent " + str(jvmRT.getHeapSizeCurrent())
        status_report += "\n  HeapSizeMax     " + str(jvmRT.getHeapSizeMax())

        threadPoolRT = server_runtime.getThreadPoolRuntime()
        status_report += "\n\n  -- Threads --"
        status_report += "\n  ExecuteThreadTotalCount " + str(threadPoolRT.getExecuteThreadTotalCount())
        status_report += "\n  ExecuteThreadIdleCount  " + str(threadPoolRT.getExecuteThreadIdleCount())
        status_report += "\n  Throughput              " + str(threadPoolRT.getThroughput())
        status_report += "\n  HoggingThreadCount      " + str(threadPoolRT.getHoggingThreadCount())
        status_report += "\n  StuckThreadCount        " + str(threadPoolRT.getStuckThreadCount())
        status_report += "\n  CompletedRequestCount   " + str(threadPoolRT.getCompletedRequestCount())
        status_report += "\n  QueueLength             " + str(threadPoolRT.getQueueLength())
        status_report += "\n"
        for thread in threadPoolRT.getExecuteThreads():
            status_report += "\n  Thread '" + thread.getName() + "' - Hogger: " + str(thread.isHogger()) + " - Current Request: " + str(thread.getCurrentRequest())

        jdbcServiceRT = server_runtime.getJDBCServiceRuntime()
        dataSources = jdbcServiceRT.getJDBCDataSourceRuntimeMBeans()
        if (len(dataSources) > 0):
            status_report += '\n\n  -- Datasources --'
            for dataSource in dataSources:
                testPool = dataSource.testPool()
                dataSourceName = dataSource.getName()
                if (testPool == None):
                    status_report += '\n\n    ' + dataSourceName+'\t'+dataSource.getState()+'\n\n'
                    status_report += "      CurrCapacity                  " + str(dataSource.getCurrCapacity()) + "\n"
                    status_report += "      ConnectionsTotalCount         " + str(dataSource.getConnectionsTotalCount()) + "\n"
                    status_report += "      ConnectionDelayTime           " + str(dataSource.getConnectionDelayTime()) + "\n"
                    status_report += "      ActiveConnectionsAverageCount " + str(dataSource.getActiveConnectionsAverageCount()) + "\n"
                    status_report += "      ActiveConnectionsCurrentCount " + str(dataSource.getActiveConnectionsCurrentCount()) + "\n"
                    status_report += "      ActiveConnectionsHighCount    " + str(dataSource.getActiveConnectionsHighCount()) + "\n"
                    status_report += "      FailuresToReconnectCount      " + str(dataSource.getFailuresToReconnectCount()) + "\n"
                    status_report += "      LeakedConnectionCount         " + str(dataSource.getLeakedConnectionCount()) + "\n"
                else:
                    status_report += '\n\n    ' + dataSourceName+'\t'+dataSource.getState()+'\tFailure: '
                    status_report += str(testPool)

    else:
        status_report += "*** No runtime information found for server: " + server.getName()
        return None

    return status_report

def show_server_status_report(server):

    server_status_report = get_server_status_report(server)
    print(server_status_report)
        
def get_server_thread_dump_report(server, repeated=False):
    
    global config_properties
    if repeated:
        thread_dump_count = int(config_properties.get('repeated_thread_dump_count', '3'))
        thread_dump_interval_seconds = int(config_properties.get('repeated_thread_dump_interval_seconds', '5'))
    else:
        thread_dump_count = 1
        thread_dump_interval_seconds = 0
    thread_dump_report = ""
    server_runtime = get_server_runtime_by_name(server.getName())
    if server_runtime is not None:
        jvmRT = server_runtime.getJVMRuntime()
        thread_dump_report += "\n\n==========  BEGIN Thread Dump for server " + server_runtime.getName() + " ==========\n"
        for i in range(thread_dump_count):
            print("Collecting thread dump " + str(i+1) + " of " + str(thread_dump_count) + " for server '" + server.getName() + "'...")
            thread_dump_report += jvmRT.getThreadStackDump()
            if i < thread_dump_count - 1:
                import java.lang.Thread as Thread
                Thread.sleep(thread_dump_interval_seconds * 1000)

        thread_dump_report += "\n\n==========  END Thread Dump for server " + server_runtime.getName() + " ==========\n"
        return thread_dump_report
    else:
        thread_dump_report += "*** No runtime information found for server: " + server.getName()
        return thread_dump_report

def build_thread_dump_filename(server):
    global config_properties
    output_files_path = config_properties.get('output_files_path', '')

    import datetime
    import os
    timestamp_text = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    thread_dump_filename = os.path.join(output_files_path, "thread_dump_" + server.getName() + "_" + timestamp_text + ".txt")

    return thread_dump_filename

def show_server_thread_dump_report(server, repeated=False):
    global config_properties

    thread_dump_report = get_server_thread_dump_report(server, repeated)

    if config_properties.get('write_thread_dump_to_file', 'false').lower() == 'true':
        thread_dump_filename = build_thread_dump_filename(server)
        try:
            with open(thread_dump_filename, 'w') as f:
                f.write(thread_dump_report)
            print("Thread dumps for server '" + server.getName() + "' had been written to file: " + thread_dump_filename)
        except Exception as e:
            print("Error writing thread dump to file: " + str(e))
            print("Printing thread dump to console instead:")
    else:
        print(thread_dump_report)

def show_server_list_status_report(server_list = []):

    if len(server_list) == 0:
        server_list = get_server_list()

    for server in server_list:
        show_server_status_report(server)

def show_server_list_thread_dump_report(server_list = []):

    if len(server_list) == 0:
        server_list = get_server_list()

    for server in server_list:
        show_server_thread_dump_report(server, repeated=False)

def show_server_list_repeated_thread_dump_report(server_list = []):

    if len(server_list) == 0:
        server_list = get_server_list()

    for server in server_list:
        show_server_thread_dump_report(server, repeated=True)

def get_server_list():

    global domain_context

    if domain_context != "config":
        domainConfig()
        domain_context = "config"

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

    global config_properties
    cluster_filter = config_properties.get('cluster_name', 'all')

    server_list = get_server_list()
    print("\nServer List:")
    if cluster_filter != 'all':
        print("filtered by cluster: " + cluster_filter)

    # Print server list in a tabular format
    print("{:<5} {:<20} {:<10} {:<10} {:<20} {:<20}".format("No.", "Name", "Port", "SSL Port", "Cluster", "Machine"))
    print("-" * 85)
    for server in server_list:

        if cluster_filter != 'all' and server.getCluster() != cluster_filter:
            continue

        print("{:<5} {:<20} {:<10} {:<10} {:<20} {:<20}".format(
            server.number,
            server.getName(),
            server.getListenPort() if server.getListenPort() is not None else 'N/A',
            server.getListenPortSSL() if server.getListenPortSSL() is not None else 'N/A',
            server.getCluster() if server.getCluster() is not None else 'N/A',
            server.getMachine() if server.getMachine() is not None else 'N/A'
        ))

        try:
            state(server.getName(),'Server')
        except Exception as e:
            print("Error retrieving server " + server.getName() + " state: " + str(e))

    print("-" * 85)
    print("\n")

def confirm_action(action_description, servers_involved):

    print("You are about to " + action_description + " the following servers:")
    for server in servers_involved:
        print("- " + server.getName())
    confirmation = raw_input("Are you sure you want to proceed? (yes/no): ")
    return confirmation.lower() == 'yes'

def filtered_server_list(server_list):
    global config_properties
    cluster_filter = config_properties.get('cluster_name', 'all')
    admin_server_name = config_properties.get('__admin_server_name', 'AdminServer')

    # Exclude Admin Server and filter by cluster if cluster filter is set
    if cluster_filter == 'all':
        return [server for server in server_list if server.getName() != admin_server_name]
    else:
        return [server for server in server_list if server.getCluster() == cluster_filter and server.getName() != admin_server_name]

def start_server(server):
     
    print "Starting server: " + server.getName()
    start(server.getName(), 'Server', block='false')

def start_server_list(server_list):

    filtered_list = filtered_server_list(server_list)

    if len(filtered_list) == 0:
        print "No servers to start after applying filters."
        return

    if confirm_action("start", filtered_list):
        for server in filtered_list:
            start_server(server)

def stop_server(server):

    print "Stopping server: " + server.getName()
    shutdown(server.getName(), 'Server', force='true', block='false')

def stop_server_list(server_list):
    filtered_list = filtered_server_list(server_list)

    if len(filtered_list) == 0:
        print "No servers to stop after applying filters."
        return

    if confirm_action("stop", filtered_list):
        for server in filtered_list:
            stop_server(server)

def create_command_executor():

    return commands.CommandExecutor(
        commands=[
            commands.Command(name='quit', description='Exit interactive mode', synonyms=['exit', 'q', 'x'], is_quit_command=True),
            commands.Command(name='list', description='Lists all servers in the domain', synonyms=['ls', 'll'], method=globals().get('show_server_list')),
            commands.Command(name='status', description='Shows status for a list of servers. If no server is specified, show status for all servers', params_description='(nothing) or [server number | server name] ... [server number | server name]', synonyms=['stat'], method=globals().get('show_server_list_status_report'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='tdump', description='Shows a single thread dump for a list of servers. If no server is specified, show the thread dump for all servers', params_description='(nothing) or [server number | server name] ... [server number | server name]', synonyms=['td'], method=globals().get('show_server_list_thread_dump_report'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='rtdump', description='Shows repeated thread dumps for a list of servers. If no server is specified, show repeated thread dumps for all servers', params_description='(nothing) or [server number | server name] ... [server number | server name]', synonyms=['rtd', 'rt'], method=globals().get('show_server_list_repeated_thread_dump_report'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='help', description='Shows this help message', synonyms=['h', '?'], is_help_command=True),
            commands.Command(name='start', description='Starts a server or a list of servers', params_description='all | [server number | server name] ... [server number | server name]', method=globals().get('start_server_list'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='stop', description='Stops a server or a list of servers', params_description='all | [server number | server name] ... [server number | server name]', method=globals().get('stop_server_list'), preprocess_parameters_method=globals().get('get_server_list_from_identifiers')),
            commands.Command(name='set', description='Shows or sets session variables. To show all session variables, run "set". To show a specific session variable, run "set [variable name]". To set a session variable, run "set [variable name] [value]"', params_description='(nothing) or [variable name] or [variable name] [value]', method=globals().get('set_session_values_report')),
            commands.Command(name='reset', description='Resets session variables to default values from config file', method=globals().get('reset_session_values_report')),
            commands.Command(name='.', description='Repeat latest command'),
        ]
    )

def set_session_values_report(parameters_sequence):

    global config_properties
 
    session_values_report = "Current session values:\n"
    if len(parameters_sequence) > 0:
        session_variable = None
        session_variable_search = parameters_sequence[0]
        session_variable_search_match_count = 0
        for variable_name, variable_value in config_properties.items():
            if variable_name.startswith(session_variable_search) and not session_variable_search.startswith('_'):
                session_variable_search_match_count += 1
                session_variable = variable_name

        if session_variable_search_match_count == 0:
            session_values_report += "No session variable found with name similar to: " + session_variable_search + "\n"
            return session_values_report

        if session_variable_search_match_count > 1:
            session_values_report += "Multiple session variables found with name similar to: " + session_variable_search + "\n"
            return session_values_report

        if len(parameters_sequence) == 1:
            session_values_report += session_variable + " = " + config_properties[session_variable] + "\n"
        elif len(parameters_sequence) == 2:
            new_session_value = parameters_sequence[1]
            config_properties[session_variable] = new_session_value
            session_values_report += "Set session variable '" + session_variable + "' to value: " + new_session_value + "\n"
        else:
            session_values_report += "Invalid number of parameters for 'set' command. To show all session variables, run 'set'. To show a specific session variable, run 'set [variable name]'. To set a session variable, run 'set [variable name] [value]'\n"
    else:
        # Show all session variable values
        for variable_name, variable_value in config_properties.items():
            if not variable_name.startswith('_'):
                session_values_report += variable_name + " = " + variable_value + "\n"
    return session_values_report

def reset_session_values_report(parameters_sequence):

    global config_properties

    load_config_properties()
    session_values_report = "Session values have been reset to default values from config file.\n"
    session_values_report += set_session_values_report([])
    return session_values_report

def interactive_loop():

    global config_properties

    command_executor = create_command_executor()

    previous_user_input = None

    while True:

        try:
            prompt = ":: "

            if config_properties.get('cluster_name', 'all') != 'all':
                prompt = "[" + config_properties.get('cluster_name') + "] " + prompt

            user_input = raw_input(prompt)

            if user_input.strip() == "":
                continue

            if user_input.strip() == ".":
                if previous_user_input is None:
                    print "No previous command to repeat."
                    continue
                else:
                    user_input = previous_user_input
                    print "Repeating command: " + user_input
            else:
                previous_user_input = user_input

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

        except NoServerFound as nsf:
            print "No server found for identifier: " + nsf.message + "\n\n"

        except Exception as e:
            print "Error in loop: " + str(e)
            print "\n"

            if config_properties.get('debug_mode', 'false').lower() == 'true':
                import traceback
                traceback.print_exc()

def process(username, password, admin_url, get_thread_dumps=False, interactive_mode=False):
            
    load_config_properties()

    ## SSL
    System.setProperty('weblogic.security.SSL.ignoreHostnameVerification', 'true')
    connect(username, password, admin_url)

    show_server_list()

    if interactive_mode:
        interactive_loop()
    else:
        show_server_list_status_report()
        if get_thread_dumps:
            show_server_list_thread_dump_report()

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