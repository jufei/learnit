from petbase import *
import pettool

def read_datadevice_config(id):
    path = os.path.sep.join([resource_path(), 'config', 'datadevice'])
    import sys, importlib
    sys.path.append(path)
    model = importlib.import_module('datadevice_%s'%(id))
    config = IpaMmlItem()
    for key in model.TOOLS_VAR:
        setattr(config, key.lower(), model.TOOLS_VAR[key])
    config.conn = None
    config.id = id
    if gv.case.curr_case.ca_type == '3CC':
        config.pppoe_conf = 'pppoe_%s_lme.conf' %(gv.tm500.tm500_id)
    elif gv.case.curr_case.ca_type == '2CC' and gv.case.curr_case.ulca:
        config.pppoe_conf = 'pppoe_%s_lme.conf' %(gv.tm500.tm500_id)
    else:
        config.pppoe_conf = 'pppoe_%s.conf' %(gv.tm500.tm500_id)
    return config

def pet_connect_to_data_device():
    if gv.datadevice:
        if not gv.datadevice.conn:
            gv.datadevice.conn = connections.connect_to_ssh_host(gv.datadevice.device_ip,
                gv.datadevice.device_port, gv.datadevice.device_username, gv.datadevice.device_password)
        else:
            connections.switch_ssh_connection(gv.datadevice.conn)

def execute_command_on_data_device(cmds):
    pet_connect_to_data_device()
    # try:
    if isinstance(cmds, list):
        output = ''
        for command in cmds:
            if command.strip():
                output += connections.execute_ssh_command_without_check(command)
        for line in output.splitlines():
            print line
        return output
    else:
        return connections.execute_ssh_command_without_check(cmds)

def stop_pppoe_on_data_device2():
    cmd = 'sshpass -p %s ssh %s@%s  -o StrictHostKeyChecking=no ps -efww |grep pppoe-connect' %(gv.datadevice.device_password, gv.datadevice.device_username,
                                                        gv.datadevice.device_ip)
    import os
    out = run_local_command_gracely(cmd)

    for conf in [x.split()[-1] for x in out.splitlines() if x.strip() and not 'grep' in x]:
        cmd = 'sshpass -p %s ssh %s@%s  -o StrictHostKeyChecking=no  pppoe-stop %s' %(gv.datadevice.device_password, gv.datadevice.device_username,
                                                            gv.datadevice.device_ip, conf)
        run_local_command_gracely(cmd)

def stop_pppoe_on_data_device():
    stop_pppoe_on_data_device2()
    cmd = 'sshpass -p %s ssh %s@%s ps -ef|grep pppoe' %(gv.datadevice.device_password, gv.datadevice.device_username,
                                                        gv.datadevice.device_ip)
    import os
    out = run_local_command_gracely(cmd)

    for pid in [x.split()[1] for x in out.splitlines() if gv.datadevice.pppoe_conf in x]:
        kw('execute_command_on_data_device', 'kill -9 '+pid)

    output = kw('execute_command_on_data_device', 'ps -ef|grep pppoe')
    for line in [x for x in output.splitlines() if gv.datadevice.pppoe_conf in x]:
        pid = line.split()[0]
        kw('execute_command_on_data_device', 'kill -9 '+pid)

    kw('execute_command_on_data_device', [ 'ifconfig -a', 'ps -ef|grep ppp', 'pppoe-stop', 'ps -ef|grep ppp', 'ifconfig -a',
        'pppoe-stop /etc/ppp/%s' %(gv.datadevice.pppoe_conf), 'ps -ef|grep ppp', 'ifconfig -a'])

def setup_pppoe_on_data_device():
    stop_pppoe_on_data_device()
    listbefore = kw('get_ppp_connection_list')
    output = kw('execute_command_on_data_device', [ 'ifconfig -a', 'ps -ef|grep ppp', 'pppoe-start /etc/ppp/%s' %(gv.datadevice.pppoe_conf), 'ps -ef|grep ppp', 'ifconfig -a'])
    time.sleep(60)
    stop_pppoe_on_data_device()
    listbefore = kw('get_ppp_connection_list')
    output = kw('execute_command_on_data_device', [ 'ifconfig -a', 'ps -ef|grep ppp', 'pppoe-start /etc/ppp/%s' %(gv.datadevice.pppoe_conf), 'ps -ef|grep ppp', 'ifconfig -a'])

    if not 'Connected'.upper() in output.upper():
        kw('log', output)
        kw('report_error', 'Setup PPPOE Failed, please check it.')
    listafter = kw('get_ppp_connection_list')
    gv.service.pppoe_name = [x for x in listafter if x not in listbefore][0]

def get_ppp_connection_list():
    output = kw('execute_command_on_data_device', "ip link show|grep ppp|grep default|awk '{print $2}'").splitlines()
    ppplist = [x.strip().replace(':', '') for x in output if 'ppp' in x]
    gv.logger.info(ppplist)
    return ppplist

def get_ftp_server_ip():
    for server in ['10.69.66.150', '10.69.66.155']:
        output = kw('execute_command_on_data_device', 'route|grep %s' %(server))
        if 'ppp' in output:
            continue
        else:
            return server
    return ''

def start_ftp_download_on_data_device():
    import time
    # time.sleep(60)
    gv.env.ftp_server = get_ftp_server_ip()
    if gv.env.ftp_server:
        kw('execute_command_on_data_device', ['cd /root/ta', './cdown.sh %s %s %s > /tmp/ftp%s.log &' %(gv.env.ftp_server,
            gv.service.pppoe_name, gv.tm500.tm500_id, gv.tm500.tm500_id)])
    else:
        kw('report_error', 'No ftp server is available')

def start_ftp_upload_on_data_device():
    import time
    # time.sleep(60)
    gv.env.ftp_server = get_ftp_server_ip()
    if gv.env.ftp_server:
        kw('execute_command_on_data_device', ['cd /root/ta', './cup.sh %s %s %s > /tmp/ftp%s.log &' %(gv.env.ftp_server,
            gv.service.pppoe_name, gv.tm500.tm500_id, gv.tm500.tm500_id)])
    else:
        kw('report_error', 'No ftp server is available')

def stop_ftp_download_on_data_device():
    kw('execute_command_on_data_device', ['ps -ef|grep pppoe', 'ifconfig -a', 'route'])
    kw('execute_command_on_data_device', "kill -9 `ps -ef|grep cdown.sh|grep %s|awk '{print $2}'`" %(gv.env.ftp_server))
    kw('execute_command_on_data_device', "kill -9 `ps -ef|grep wget|grep %s|awk '{print $2}'`" %(gv.env.ftp_server))

def stop_ftp_upload_on_data_device():
    kw('execute_command_on_data_device', ['ps -ef|grep pppoe', 'ifconfig -a', 'route'])
    kw('execute_command_on_data_device', "kill -9 `ps -ef|grep cup.sh|grep %s|awk '{print $2}'`" %(gv.env.ftp_server))
    kw('execute_command_on_data_device', "kill -9 `ps -ef|grep ftp|grep %s|awk '{print $2}'`" %(gv.env.ftp_server))

def cleanup_ftp_on_data_device():
    kw('run_keyword_and_ignore_error', 'stop_ftp_download_on_data_device')
    kw('run_keyword_and_ignore_error', 'stop_ftp_upload_on_data_device')
    kw('run_keyword_and_ignore_error', 'stop_pppoe_on_data_device')


def pet_data_device_is_free(dd_id):
    config = read_datadevice_config(dd_id)
    conn = connections.connect_to_ssh_host(config.device_ip, config.device_port, config.device_username, config.device_password)
    output = connections.execute_ssh_command_without_check('dir')
    output = connections.execute_ssh_command_without_check('netstat -na|grep 30001')
    connections.disconnect_from_ssh()
    return False if 'LISTEN' in output else True

def pet_occupy_data_device(timeout = '900'):
    pet_connect_to_data_device()
    connections.execute_ssh_command_without_check('nohup python /root/ta/resmgr.py >/dev/null -t %s &' %(timeout))
    gv.logger.info('Start to occupy Datadevice , timeout: [%s]' %(timeout))

def pet_release_data_device():
    if not gv.smart_device:
        return
    if gv.datadevice.conn:
        output =  kw('execute_command_on_data_device', 'ps -ef|grep resmgr.py')
        line = [x for x in output.splitlines() if 'resmgr.py' in x and not 'color' in x]
        if line:
            kw('execute_command_on_data_device', 'kill -9 ' + line[0].split()[1])

def select_datadevice():
    if not gv.smart_device:
        gv.datadevice = kw('read_datadevice_config', pv('Datadevice'))
    else:
        dd_list = pv('Datadevice').replace(';', ',').split(',')
        for device in dd_list:
            selected = False
            if kw('pet_data_device_is_free', device):
                print 'Selected Datadevice: '+ device
                gv.datadevice = kw('read_datadevice_config', device)
                kw('pet_occupy_data_device')
                return
            else:
                print 'Datadevice %s is not free, try next ...' %(device)
        kw('report_error', 'No Datadevice is available for this case, case will fail.')
