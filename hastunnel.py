import os
import time
import yaml
import json
import socket
import subprocess
from datetime import datetime
from datetime import timezone

config = yaml.safe_load(os.environ.get('HASTUNNEL_CONFIG'))


def get_next_backend(backends=[]):
    for backend in backends:
        host = backend.split(':')[0]
        port = backend.split(':')[1]
        if check_tcp(host, port):
            return backend
    return backends[0]


def check_tcp(host, port):
    port = int(port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False


def write_stunnel_conf(config):
    lines = ['debug = 3', '']
    services = config["services"]
    for service_name in services:
        service = services[service_name]
        listen_port = service['listen_port']
        backend = get_next_backend(service['backends'])
        if backend:
            lines.append('[' + service_name + ']')
            lines.append('client = yes')
            lines.append('securityLevel = 0')
            lines.append('accept = ' + str(listen_port))
            lines.append('connect = ' + backend)
            lines.append('')
    f = open('/stunnel.conf', 'w')
    f.writelines('%s\n' % i for i in lines)
    f.close


def get_backends(config):
    backends = []
    services = config["services"]
    for service_name in services:
        service = services[service_name]
        backends.append(get_next_backend(service['backends']))
    backends.sort()
    return backends


def run_foreground(cmd):
    return subprocess.run(cmd, encoding='utf-8',
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_background(cmd):
    return subprocess.Popen(cmd)


def run_stunnel():
    cmd = ['pgrep', 'stunnel']
    o = run_foreground(cmd)
    for pid in o.stdout.strip().split("\n"):
        cmd = ['kill', pid]
        run_foreground(cmd)
    cmd = ['stunnel', '/stunnel.conf']
    run_background(cmd)


backends = get_backends(config)
print(datetime.now(tz=timezone.utc).isoformat()
      + ' using backends ' + json.dumps(backends), flush=True)
write_stunnel_conf(config)
run_stunnel()
while True:
    if json.dumps(backends) != json.dumps(get_backends(config)):
        backends = get_backends(config)
        print(datetime.now(tz=timezone.utc).isoformat()
              + ' using backends ' + json.dumps(backends), flush=True)
        write_stunnel_conf(config)
        run_stunnel()
    time.sleep(2)
