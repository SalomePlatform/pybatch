import sys
import socket

expected_lines = int(sys.argv[1])
with open("batch_nodefile.txt", "r") as f:
    hosts = f.readlines()
nb_hosts = 0
for host in hosts:
    if host:  # skip empty lines
        socket.gethostbyname(host.strip())  # check valid hostname
        nb_hosts += 1
assert expected_lines == nb_hosts
