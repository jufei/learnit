from petbase import *
import logging
import datetime
import select
from thread import *
import threading
import socket

def btslog_monitor_thread(btslogger):
    def _get_filename():
        return os.sep.join([btslogger.working_dire, 'btslog_%s_%s.log' % (btslogger.bts.btsid, time.strftime("%d__%H_%M_%S"))])
    buf = ''
    fatal_str = ''
    fatal_time = 0
    found_fatal = False
    filename = _get_filename()
    max_size = 8192

    if gv.case.done:
        return 0
    if btslogger.conn_btslog:
        btslogger.conn_btslog.setblocking(0)
    else:
        return 0

    while True:
        now = datetime.datetime.now()
        ret = ''
        if btslogger.conn_btslog:
            try:
                ready = select.select([btslogger.conn_btslog], [], [], 900)
            except:
                return 0

            if ready[0] and btslogger.conn_btslog:
                ret = btslogger.conn_btslog.recv(max_size)

            if ret:
                buf += ret
                if len(ret) == max_size:
                    recvdata = buf.splitlines()[:-1]
                    buf = buf.splitlines()[-1]
                else:
                    recvdata = buf.splitlines()
                    buf = ''
                recvdata = [line.strip().replace(chr(0), '') for line in recvdata if line.strip()]
                if os.path.exists(filename):
                    if os.path.getsize(filename) >= 1024*1024*100:
                        import zipfile
                        z = zipfile.ZipFile(filename.replace('.log', '_t.zip'), 'w')
                        z.write(filename, os.path.basename(filename), zipfile.ZIP_DEFLATED)
                        os.remove(filename)
                        z.close()
                        filename = _get_filename()
                with open(filename, 'a') as f:
                    for line in recvdata:
                        if line.strip():
                            f.write('[%s]  %s\n' % (now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], line))

                if btslogger.care_btslog:
                    btslogger.buffer += recvdata

                if 'fatal'.upper() in ret.upper()  and\
                     not 'Non fatal'.upper() in ret.upper() and\
                     not 'FaultAddress'.upper() in ret.upper() and\
                     not 'fatalfaultaddress'.upper() in ret.upper():
                    self.logger.info('Found Fatal: ' + ret)
                    fatal_str = ret
                    fatal_time = time.time()
                    found_fatal = True

                if found_fatal:
                    if time.time() - fatal_time > 10:
                        gv.suite.health = False
                        gv.case.monitor_error_msg = 'Fatal found in BTSlog: [%s]. ' % (str(fatal_str))
                        return 0
        else:
            return 0


class c_pet_btslogger(object):
    def __init__(self, bts, working_dire):
        self.bts = bts
        self.port = 30003
        self.logger = logging.getLogger(__file__)
        self.care_btslog = False
        self.conn_btslog = None
        self.lock_btslog = None
        self.buffer = []
        self.working_dire = working_dire

    def start_remote_server(self):
        output = self.bts.conn_pc.execute_command('netstat -nao|grep 30003')
        for line in output.splitlines():
            if 'LISTENING' in line:
                pid = line.split()[-1]
                self.bts.conn_pc.execute_command('taskkill /PID %s /F' % (pid))
        cmd = 'psexec -i -d -u %s -p %s c:\\python27\\python  c:\\python27\\btslog_pcap.py' %\
                 (self.bts.config.bts_control_pc_username, self.bts.config.bts_control_pc_password)
        cmd += ' -i %s -s 51000 ' % (self.bts.config.pcap_interface)
        self.logger.info(cmd)
        self.bts.conn_pc.execute_command(cmd)
        self.bts.conn_pc.wait_until_port_is_listening('30003', '40')
        self.bts.conn_pc.execute_command('netstat -nao|grep 30003')

    def setup(self):
        self.start_remote_server()
        self.conn_btslog = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_btslog.connect((self.bts.config.bts_control_pc_lab, 30003))
        self.lock_btslog = threading.Lock()
        start_new_thread(btslog_monitor_thread , (self, ))

    def start_to_care(self):
        with self.lock_btslog:
            self.buffer = []
            self.care_btslog = True

    def stop_to_care(self):
        with self.lock_btslog:
            self.buffer = []
            self.care_btslog = False

    def teardown(self):
        if self.conn_btslog:
            with self.lock_btslog:
                self.conn_btslog.close()
                self.conn_btslog = None
        import zipfile
        for btslog in [filename for filename in os.listdir(self.working_dire) if 'btslog_%s_' %(self.bts.btsid) in filename and '.log' in filename]:
            zipfilename = os.sep.join([self.working_dire, btslog.replace('.log', '.zip')])
            z = zipfile.ZipFile(zipfilename, 'w')
            z.write(os.sep.join([self.working_dire, btslog]), os.path.basename(btslog), zipfile.ZIP_DEFLATED)
            os.remove(os.sep.join([self.working_dire, btslog]))
            z.close()

if __name__ == '__main__':
    pass
