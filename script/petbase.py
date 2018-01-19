import time, os, datetime, sys
import random
from robot.libraries import BuiltIn
from robot.running.context import EXECUTION_CONTEXTS
import threading
import signal
import logging
import traceback
from lxml import etree

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pet_ipalib import *
import PetShell.connections as connections
from PetShell.file_lib.xml_control import change_xml_file, get_vendor_version
from PetShell.file_lib.xml_control import common_xml_operation, ParseXML

def pv(varname):
    if not '$' in varname:
        varname = '${%s}' %(varname)
    builtin = BuiltIn.BuiltIn()
    return builtin.get_variables()[varname]

def spv(varname, value):
    if not '$' in varname:
        varname = '${%s}' %(varname)
    builtin = BuiltIn.BuiltIn()
    builtin.set_suite_variable(varname, value)

def in_robot():
    return EXECUTION_CONTEXTS.current is not None

def var_exist(varname):
    if not '$' in varname:
        varname = '${%s}' %(varname)
    builtin = BuiltIn.BuiltIn()
    return varname in builtin.get_variables().keys()

def save_log(lines = [], filename = '', with_time = 'Y'):
    import datetime
    now = datetime.datetime.now()
    with open(filename, 'a') as f:
        for line in lines:
            if with_time == 'Y':
                f.write('%s  %-100s *****\n' %(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], line.replace('\n', '')))
            else:
                f.write(line.replace('\n', '') +'\n')

def pathc(path):
    return path.replace('\\', '\\\\')

def kw(kwname, *args):
    if gv.pythonmode:
        t = globals().keys()
        t.sort()
        if kwname in globals().keys():
            if kwname.lower() in ['log']:
                builtin = BuiltIn.BuiltIn()
                return builtin.run_keyword(kwname, *args)
            else:
                return globals()[kwname](*args)
    else:
        builtin = BuiltIn.BuiltIn()
        return builtin.run_keyword(kwname, *args)

from robot.api import logger
def write_to_console(s):
    logger.console(s)

def to_winpath(unixpath):
    return unixpath.replace('/', r'\\')

def kwg(keyword_name='', *args):
    gv.case.keyword_group.append(keyword_name, *args)

def suite_file(filename):
    return os.sep.join([gv.suite.log_directory, filename])

def bts_file(btsid, filename):
    return os.sep.join([gv.suite.log_directory, 'BTS'+btsid, filename])

def bts_source_file(btsid, filename):
    if filename == '':
        return os.path.sep.join([resource_path(), 'config', 'bts', 'BTS'+btsid])
    else:
        return os.path.sep.join([resource_path(), 'config', 'bts', 'BTS'+btsid, filename])

def tm500_source_file(filename):
    return os.path.sep.join([resource_path(), 'config', 'tm500', filename])

def case_file(filename):
    return os.sep.join([gv.case.log_directory, filename])

def resource_path():
    return os.path.abspath(os.path.dirname(__file__))

def counter_file(filename):
    return os.sep.join([gv.case.log_directory, 'counter', filename])

def case_has_tag(tagname):
    builtin = BuiltIn.BuiltIn()
    tags = kw('create list', '@{Test Tags}')
    return tagname.upper().strip() in [x.upper().strip() for x in tags]

def contain_keywords(mainstr = '', keywords = [], except_keywords = []):
    lines = []
    for line in mainstr.splitlines():
        if len([keyword for keyword in except_keywords if keyword.upper() in line.upper()]) >0:
            continue
        else:
            if len([keyword for keyword in keywords if keyword.upper() in line.upper()]) >0:
                lines.append(line)
    return lines

def addlog(astr, log):
    for line in astr.splitlines():
        log.append('%s --- %s\n' %(time.ctime(), line))

def record_tm500log(astr):
    addlog(astr, gv.tm500.output)

def record_debuginfo(astr):
    with open(gv.case.debug_file,'a') as f:
        import datetime
        now = datetime.datetime.now()
        for line in astr.splitlines():
            gv.logger.info(line)
            f.write('*****%s  %-100s *****\n' %(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], line))

def record_monitor_info(astr):
    with open(case_file('monitor.log'),'a') as f:
        import datetime
        now = datetime.datetime.now()
        for line in astr.splitlines():
            f.write('*****%s  %-20s *****\n' %(now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], line))

def _stop_execution(signum, frame):
    from robot.running import EXECUTION_CONTEXTS
    from robot.running.keywords import Keyword
    gv.env.save_snapshot = True
    Keyword('report_error', (gv.case.monitor_error_msg,)).run(EXECUTION_CONTEXTS.current)

def prepare_for_thread_work():
    signal.signal(signal.SIGUSR1, _stop_execution)

def quit_thread_with_error_message(msg):
    gv.case.monitor_error_msg = msg

def check_btslog_fatal():
    if gv.case.monitor_error_msg:
        kw('log', 'Found Fatal!!!!')
        kw('report_error', gv.case.monitor_error_msg)

def has_attr(item, attrname):
    return attrname.upper() in [x.upper() for x in dir(item)]

def case_has_attr(attrname):
    return attrname.lower() in [x.lower().strip() for x in dir(gv.case.curr_case)]

def case_has_tag(tagname):
    return tagname.lower() in [x.lower() for x in gv.case.tags]

def run_local_command(cmd):
    gv.logger.info('Run local command: %s' %(cmd))
    for line in os.popen(cmd).readlines():
        gv.logger.info(line)

def run_local_command_gracely(cmd):
    import subprocess
    gv.logger.info('Run local command: %s' %(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=open(os.devnull,'w'), shell=True)
    out, error = p.communicate()
    if out:
        gv.logger.info('command output: [%s]' %(out))
    if error:
        gv.logger.error('command error: [%s]' %(error))
    return out

def read_excel_sheet(filename, sheetname):
    import xlrd
    bk = xlrd.open_workbook(filename)
    shxrange = range(bk.nsheets)
    sh = bk.sheet_by_name(sheetname)
    nrows, ncols = sh.nrows, sh.ncols
    titles = sh.row_values(0)
    info = []
    for i in range(1, nrows):
        line = ['%s' % (x) for x in sh.row_values(i)]
        acase = IpaMmlItem()
        acase.mode = 1
        if line[0].strip():
            for j in range(len(titles)):
                if titles[j].strip():
                    setattr(acase, titles[j].lower().strip(), '%s' % (line[j].replace('.0','').strip()))
        info.append(acase)
    return info


def caseis(attname = '', value = ''):
    if value:
        return value == getattr(gv.case.curr_case, attname)
    else:
        return getattr(gv.case.curr_case, attname)

def case_attr(attrname):
    return str(getattr(gv.case.curr_case, attrname)).strip()

def print_in_table(lines):
    output = ['<TABLE BORDER=1 BORDERCOLOR="#000000" CELLPADDING=4 CELLSPACING=0>']
    for i in range(len(lines)):
        output.append('<tr>')
        tstr = 'th' if i == 0 else 'td'
        for item in lines[i].split('|'):
            if item.strip():
                output.append('<%s>%s</%s>' %(tstr, item, tstr))
        output.append('</tr>')
    output.append('</table>')
    print "*HTML* \n%s" %('\n'.join(output))

def try_best_to_connect_ssh(host, port, username, password):
    prompt = ''
    from pettool import get_ssh_prompt
    try:
        prompt = get_ssh_prompt(host, int(port), username, password)
        print 'Found prompt: [%s]' %(prompt)
    except:
        print 'Warning: get prompt failed'
        pass
    if prompt <> '':
        conn = connections.connect_to_ssh_host(host, port, username, password, prompt)
        return conn
    else:
        try:
            conn = connections.connect_to_ssh_host(host, port, username, password, '#')
        except:
            try:
                conn = connections.connect_to_ssh_host(host, port, username, password, '>')
            except:
                raise Exception, 'Connect to SSH Host failed.'
    return conn


class c_global_var_list(object):
    def __init__(self):
        self.suite                  =   IpaMmlItem()
        self.suite.health           =   True
        self.suite.suite_index      =   0

        self.case                   =   IpaMmlItem()
        self.case.case_index        =   0
        self.case.done              =   False
        self.case.in_teardown       =   False
        self.case.start_testing     =   False
        self.case.service_done      =   False
        self.case.debug_file        =   ''
        self.case.case_log_list     =   []
        self.case.cmd_list          =   []
        self.case.monitor_error_msg =   ''

        self.env = IpaMmlItem()
        self.env.use_ixia                           =   False
        self.env.use_tm500                          =   True
        self.env.use_infomodel                      =   True
        self.env.use_catapult                       =   False
        self.env.use_prisma                         =   False
        self.env.need_upgrade_tm500                 =   False
        self.env.use_single_oam                     =   False
        self.env.save_snapshot                      =   False
        self.env.restart_bts_for_each_case          =   False
        self.env.restart_tm500_for_each_case        =   False
        self.env.ftp_server                         =   ''
        self.env.release                            =   ''
        self.env.bts_version                        =   ''
        self.env.scf_changing                       =   {}
        self.env.card_band                          =   ''

        self.service                                = IpaMmlItem()
        self.service.pppoe_name                     =   ''
        self.service.ue_ip                          =   ''

        self.kpi                            =   IpaMmlItem()
        self.kpi.kpi_volte_call_drop_ratio  =   'INVALID'

        self.tti                            =   IpaMmlItem()
        self.tti.process                    =   ''
        self.tti.core_info                  =   ''
        self.tti.stream                     =   ''
        self.tti.ttiparser                  =   ''
        self.tti.tti_process                =   ''


        self.debug_mode = False

        self.master_bts = None
        self.slave_bts = None
        # self.allbts = []
        self.tm500      = None
        self.ixia       = None
        self.artiza     = None

        self.datadevice = IpaMmlItem()

        self.smart_device = False
        self.pythonmode = False

        self.logger = logging.getLogger(__file__)
        logging.basicConfig(    format='%(asctime)s,%(msecs)d [TA_%(levelname)s] %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.DEBUG)
        # self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)
        self.shenick_groups = []

        self.prisma = None
        self.prisma_runner = None
        self.adb = None
        self.counter_result = None
        self.counter_manager = None
        self.conn_agent = None

        self.allbts = []

    def mbts(self): #standalone bts list of master bts or master bts itself
        return [x for x in gv.allbts if x.role == 'M']

    def sbts(self):
        return [x for x in gv.allbts if x.role == 'S']


gv = c_global_var_list()


if __name__ == '__main__':
    pass
