import os, sys
import time, datetime
import traceback
import pet_bts
from petbase import *
import PetShell.connections as connections

target_port = (['192.168.255.1','12345','tcp'],
               ['192.168.255.1','12347','tcp'],
               ['192.168.255.1','15007','tcp'],
               ['192.168.255.1','15003','tcp'],
               ['192.168.255.1','6001','tcp'],
               ['192.168.255.1','9002','tcp'],
               ['192.168.255.129','3600','tcp'],
               ['192.168.255.129','443','tcp'])

def get_config_path(bts_id):
    pet_bts.connect_to_bts_control_pc(bts_id)
    output = connections.execute_shell_command_without_check("wmic process where name='PassPort.exe' get ProcessID, ExecutablePath")
    for line in output.splitlines():
        if '\passport.exe' in line.lower():
            path = line.split(r'\PassPort.exe')[0]

            print path
            return path


def gene_config_file(bts):
    pet_bts.connect_to_bts_control_pc(bts.btsid)
    path = get_config_path(bts.btsid)
    root_disc = path.split(r'\Program Files')[0]
    connections.execute_shell_command_without_check("%s"%(root_disc))
    connections.execute_shell_command_without_check("cd %s"%(path))
    config_content = '^<?xml version="1.0" encoding="utf-8"?^>^<PassPort^>'
    config_path = 'PassPortConfig.xml'
    connections.execute_shell_command_without_check("echo %s > %s"%(config_content,config_path))
    for i in target_port:
        config = '^<Forward^>^<Source address="%s" port="%s" /^>^<Target address="%s" port="%s" /^>^<Protocol type="%s" /^>^</Forward^>'%(bts.bts_control_pc_lab,i[1],i[0],i[1],i[2])
        print config
        connections.execute_shell_command_without_check("echo %s >> %s"%(config,config_path))
        # config_content += config
    config_content = '^</PassPort^>'
    connections.execute_shell_command_without_check("echo %s >> %s"%(config_content,config_path))


def prepare_passport_config(bts_id):
    bts = pet_bts.read_bts_config(bts_id)
    restart_passport(bts_id)
    # print check_port_listening(bts)
    if not check_port_listening(bts_id):
        gene_config_file(bts)
        restart_passport(bts_id)
    else:
        print 'Passport config is ok!'

def restart_passport(bts_id):
    pet_bts.connect_to_bts_control_pc(bts_id)
    servicename = '"PassPort (port forwarding)"'
    output = connections.execute_shell_command_without_check('sc query ' + servicename)
    if not 'RUNNING' in output:
        return connections.execute_shell_command_without_check('sc start ' + servicename)
    else:
        connections.execute_shell_command_without_check('sc stop ' + servicename)
        time.sleep(1)
        connections.execute_shell_command_without_check('sc start ' + servicename)


def check_port_listening(bts_id):
    pet_bts.connect_to_bts_control_pc(bts_id)
    for num_port in target_port:
        output = connections.execute_shell_command_without_check('netstat -na|grep %s' %(num_port[1]))
        if 'LISTENING' in output:
            continue
        else:
            print 'fail to find port [%s] listening' %(num_port[1])
            return False
    return True


if __name__ == '__main__':
    bts = pet_bts.read_bts_config('1724')
    gv.allbts =[]
    gv.allbts.append(bts)
    prepare_passport_config('1724')



