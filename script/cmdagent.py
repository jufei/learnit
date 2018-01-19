#!/usr/bin/env python
import subprocess
import time, socket, sys
from  optparse import *
import os
from thread import *
from pet_ipalib import IpaMmlItem

from threading  import Thread
from Queue import Queue, Empty

def log(info):
    with open(gv.logfile, 'a') as logf:
        logf.write('%s %s %s\n' %(time.ctime(), gv.master, info))

gv = IpaMmlItem()
gv.done = False
gv.master = ''

def commandthread(sock):
    allprocess = []
    def _cleanup():
        try:
            for handler in allprocess:
                try:
                    os.system('kill -9 '+handler.process.pid)
                except:
                    pass
        except:
            pass
        gv.done = True

    while True:
        if time.time() - gv.inittime > gv.timeout:
            log('Client timeout, Server will quit')
            _cleanup()
            return 0

        try:
            line = sock.recv(4096)
        except:
            log('Connection lost')
            _cleanup()
            return 0

        if line.strip():
            log('Received : %s' %(line))

            if line.strip().lower() == 'quit':
                log("client quit")
                sock.close()
                _cleanup()
                return 0

            if line.strip().lower() == 'log':
                log("log: %s" %(' '.join(line.split()[1:])))

            if line.lower().startswith('run'): # run iperf xx dda xx - daf
                cmdhander = IpaMmlItem()
                cmd = ' '.join(line.split()[1:])

                import datetime
                tracefile = os.sep.join(['/home/work/temp/ta', datetime.datetime.now().strftime('%M%S%f.log')])
                if os.path.exists(tracefile):
                    os.system('rm -rf ' + tracefile)
                cmd += ' >' + tracefile
                cmdhander.command = cmd
                log('Run command: [%s]' %(cmd))
                cmdhander.process = subprocess.Popen(cmd, stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                    shell=True)

                output = []
                for i in range(5):
                    if os.path.exists(tracefile):
                        output = open(tracefile).readlines()
                        break
                    else:
                        time.sleep(1)

                for line in output:
                    log('Process output:  ' + line.splitlines()[0])

                if os.path.exists(tracefile):
                    os.system('rm -rf ' + tracefile)
                sock.sendall('PID: ' +str(cmdhander.process.pid)+'  done')
                log('Process ID:  %s' %(cmdhander.process.pid))
                allprocess.append(cmdhander)

            if line.lower().startswith('stop'):
                pid = line.split()[1].strip()
                cmdhander = [x for x in allprocess if str(x.process.pid) == pid]
                if cmdhander:
                    log('Try to stop pid: ' + pid)
                    import signal
                    cmdhander[0].process.send_signal(signal.SIGINT)
                    log('Stop process: %s' %(cmdhander[0].process.pid))

            if line.lower().startswith('sendkey'):
                pid = line.split()[1].strip()
                cmdhander = [x for x in allprocess if str(x.process.pid) == pid]
                if cmdhander:
                    key = line.split()[2].strip()
                    log('Send key process: %s' %(cmdhander[0].process.pid))
                    if key.lower() == 'return':
                        log('POLL: [%s]' %(str(cmdhander[0].process.poll())))
                        if cmdhander[0].process.poll() == None:
                            try:
                                cmdhander[0].process.stdin.write('\n')
                                log(str(cmdhander[0].process.communicate()))
                            except:
                                log('Process communicate failed.')
                        log('Deal with key done.')
                        allprocess.remove(cmdhander[0])
                    else:
                        cmdhander[0].process.stdin.write(key)

def cleanup_for_process():
    pidlist = []
    output  = os.popen('lsof -i tcp:%s|grep LISTEN' %(gv.port)).readlines()
    output += os.popen('lsof -i tcp:%s|grep CLOSE_WAIT' %(gv.port)).readlines()
    pidlist = [line.split()[1] for line in output if not str(gv.pid) in line and not 'color' in line]
    for pid in list(set(pidlist)):
        cmd = 'kill -9 '+ pid
        log('Cleanup related process: '+cmd)
        try:
            os.system(cmd)
        except:
            pass

def no_client_connection():
    output = os.popen(' netstat -na|grep %s|grep ESTABLISHED' %(gv.port)).readlines()
    return len(output) == 0

def main(args = sys.argv[1:]):
    parser = OptionParser()
    parser.add_option("-m",  dest="master", default='', help='master name who call the agent, ex: BTS138')
    parser.add_option("-p",  dest="port", default='6000', help='agent listen port')
    parser.add_option("-t",  dest="timeout", default='3600', help='timeout in second')
    (options, args) = parser.parse_args()
    gv.timeout = int(options.timeout)
    gv.port = options.port
    gv.pid = os.getpid()
    gv.master = options.master
    gv.logfile = '/home/work/temp/ta/%scmd.log' %(gv.master)
    try:
        RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", int(options.port)))
        server_socket.listen(10)
        log('')
        log('Starting agent server on port ' + options.port)
        sockfd, addr = server_socket.accept()
        gv.done = False
        gv.inittime = time.time()
        start_new_thread(commandthread ,(sockfd,))
        log('connected from: (%s, %s)]' %(addr))
        while gv.done == False:
            time.sleep(3)
            if no_client_connection():
                log('No client connection, quit.')
                break
            if time.time() - gv.inittime > gv.timeout:
                log('Server timeout, Server will quit')
                break
    finally:
        server_socket.close()
        cleanup_for_process()

if __name__ == '__main__':
    main()
