class Server:
    def __init__(self, name, listen_port, listen_port_ssl, cluster, machine):
        self.name = name
        self.listen_port = listen_port
        self.listen_port_ssl = listen_port_ssl
        self.cluster = cluster
        self.machine = machine

    def getName(self):
        return self.name

    def getListenPort(self):
        return self.listen_port

    def getListenPortSSL(self):
        return self.listen_port_ssl

    def getCluster(self):
        return self.cluster

    def getMachine(self):
        return self.machine
        