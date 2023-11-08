import telnetlib
import paramiko
import socket

class InterfaceEquipment:
    def __init__(self, ip='', user='', password='', cli_type='SSH'):
        self.login_user = user
        self.login_pass = password
        self.login_ip = ip
        self.cli_type = cli_type

        self.clientSSH = paramiko.SSHClient()
        self.clientSSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.clientTelnet = telnetlib.Telnet()
        self.sshSession = None

        self.cod_error = ""

    def check_ports(self, ip, port):
        portTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        portTest.settimeout(1)
        if portTest.connect_ex((ip, port)) == 0:
            portTest.close()
            return True
        else:
            return False

    def connect(self):
        if self.cli_type == 'SSH':
            try:
                self.clientSSH.connect(self.login_ip, username=self.login_user, password=self.login_pass, timeout=2, look_for_keys=False)
                return True
            except Exception as e:
                self.cod_error = e
                return False
        elif self.cli_type == 'TELNET':
            try:
                self.clientTelnet.open(self.login_ip)
                self.clientTelnet.read_until("login: ", timeout=2)
                self.clientTelnet.write(self.login_user + "\n")
                self.clientTelnet.read_until("Password: ", timeout=2)
                self.clientTelnet.write(self.login_pass + "\n")
                if self.clientTelnet.read_until('#', timeout=2).find("#") != -1:
                    return True
                else:
                    return self.tryConnections()
            except Exception as e:
                self.cod_error = e
                return False
        else:
            return self.tryConnections()

    def tryConnections(self):
        # Teste de portas
        if self.checkPorts(self.login_ip, 22):
            self.cli_type = 'SSH'
        elif self.checkPorts(self.login_ip, 23):
            self.cli_type = 'TELNET'
        else:
            self.cli_type = 'indeterminado'
        print('TODO: tipo de login identificado: '+self.cli_type) #TODO

    def send_command_default(self, cmd):
        _stdin, _stdout,_stderr = self.clientSSH.exec_command(cmd)
        return _stdout.read().decode()

    def send_command(self, cmd):
        if self.cli_type == 'SSH':
            while self.sshSession.recv_ready():
                self.sshSession.recv(1024)
            self.sshSession.sendall(cmd + '\n')
            output = ''
            while not self.sshSession.recv_ready():
                pass
            while self.sshSession.recv_ready():
                try:
                    och = self.sshSession.recv(1024)
                    output += och.decode("utf-8")
                except:
                    return output
            return output
        elif self.cli_type == 'TELNET':
            self.clientTelnet.write(cmd + "\n")
            saida = self.clientTelnet.read_until('#', timeout=5)
            if saida.find('--More') != -1:
                return saida
            else:
                s = True
                while s:
                    self.clientTelnet.write(" \n")
                    maisSaida = self.clientTelnet.read_until('#', timeout=5)
                    saida += maisSaida
                    if maisSaida.find('#') != -1:
                        s = False
                return saida
        else:
            return None

    def disconnect(self):
        if self.cli_type == 'SSH':
            self.clientSSH.close()
        elif self.cli_type == 'TELNET':
            self.clientTelnet.close()
        else:
            pass

