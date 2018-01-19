# -*- coding: utf-8 -*-
from petbase import *
import logging
import time
import datetime

sm_command_response = {
    'module':       'Module operation was COMPLETED',
    'link':       'I/F Modules operation was COMPLETED',
    'set':       'Setting operation was COMPLETED',
    'cellsearch':       'Cell Search operation was COMPLETED',
    'box':       'Box operation was COMPLETED',
    'sef':       'SEF Setting operation was COMPLETED',
    'close':       'Close operation was COMPLETED',
    'sim -a start':       'Simulation operation was COMPLETED',
    'sim -a stop':       'Simulation operation was COMPLETED',
    'textout':       'Textout operation was COMPLETED',
    'burst':       'Burst Call operation was COMPLETED',
}


class c_pet_system_manager(object):

    def __init__(self, artiza):
        self.artiza = artiza
        self.conn = None
        self.timer = 300
        self.logfile = '/tmp/artiza.log'
        # self.logger = artiza.logger
        self.logger = logging.getLogger(__name__)
        self.stat_result = IpaMmlItem()
        self.stat_result.cplan_history = []

    def connect(self):
        if not self.conn:
            self.logger.info('Try to connect System Manager ...')
            self.conn = connections.connect_to_host(self.artiza.config.sm_ip,
                                                    str(self.artiza.config.sm_port))
            time.sleep(1)
        connections.switch_host_connection(self.conn)

    def is_running(self):
        output = self.artiza.execute_command_on_cpc('tasklist |grep SystemManager.exe')
        return len([line for line in output.splitlines() if line and 'SystemManager' in line and not 'grep' in line]) <> 0

    def is_servermode(self):
        output = self.artiza.execute_command_on_cpc('netstat -na|grep %s|grep LISTENING' % (self.artiza.config.sm_port))
        return len([line for line in output.splitlines() if line and not 'grep' in line]) <> 0

    def start_app(self):
        cmd = 'client localhost %s /server' % (self.artiza.config.sm_application)
        self.artiza.connect_to_cpc()
        try:
            connections.excute_shell_command_bare(cmd)
            time.sleep(5)
            for i in range(5):
                connections.execute_shell_command_without_check('\x03')
        except:
            pass
        timeout = 40
        for i in range(timeout):
            if self.is_servermode():
                return 0
            else:
                time.sleep(1)
        raise Exception, 'Failed to Start System Manager in [%s] seconds' % (timeout)

    def disconnect(self):
        if self.conn:
            connections.switch_host_connection(self.conn)
            connections.disconnect_from_host()
            self.conn_sm = None

    def set_logfile(self, filename):
        self.logfile = filename

    def save_log(self, output):
        if self.logfile:
            now = datetime.datetime.now()
            with open(self.logfile, 'a') as f:
                for line in [x for x in output.splitlines() if not 'RF Unit' in x]:
                    if line.strip():
                        f.write('%s  %-100s\n' % (now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], line.replace('\n', '')))
        else:
            self.conn._log("No System Manager output file name")

    def read_output(self, timeout=0):
        self.connect()
        delay_timeout = float(timeout)
        if delay_timeout > 0:
            output = ''
            st = time.time()
            while (True):
                buf = self.conn.read_very_eager()
                if buf:
                    self.save_log(buf)
                    output += buf
                if time.time() - st > delay_timeout:
                    break
                time.sleep(0.01)
        else:
            output = self.conn.read_very_eager()
            self.save_log(output)
        return output

    def execute_sm_command_and_wait_until_done(self, command='', timer=300, ignore_error=False, command_interval=30):
        command_ack = '%s command ok'
        smcommand = command.split()[0]
        command_done = sm_command_response[smcommand] if smcommand in sm_command_response else ''
        command_done = 'Simulation operation was COMPLETED' if 'sim -a' in command else command_done
        command_done = 'Burst Call operation was COMPLETED' if 'sim -a' in command else command_done
        command_done = 'Get Stat operation was COMPLETED' if 'getstat' in command else command_done
        self.logger.info('Execute Artiza Command: [%s], Waiting for : [%s]' % (command, command_done))

        self.connect()
        self.read_output()
        self.conn.write(command + '\r\n')
        time.sleep(0.5)
        ret = self.conn.read_eager()
        self.save_log(command + '\n' + ret)
        if command_ack.upper() in ret.upper():
            raise Exception, 'Could not find the command ACK [%s]' % (command_ack)
        if command_done.upper() in ret.upper():
            return ret

        st = time.time()
        while (True):
            buf = self.conn.read_very_eager()
            if buf:
                ret += buf
                self.save_log(buf)
                if 'FAILURE' in ret.upper() or 'ERROR' in ret.upper():
                    line = [x for x in ret.splitlines() if 'FAILURE' in x.upper() or 'ERROR' in x.upper()]
                    line = line[0] if line else ''
                    if not ignore_error:
                        raise Exception, 'Found error in System Manager Output: [%s]' % (line)
                    else:
                        print 'Found error in System Manager Output: [%s], ignored' % (line)
                        break
                if command_done.upper() in ret.upper():
                    break
                if time.time() - st > timer:
                    msg = "Command [%s] Timeout [%d]seconds! " % (command, timer)
                    self.logger.warning(msg)
                    ret += msg
                    return ret.upper()
                    break
            time.sleep(0.01)
        self.logger.info('Command Done, rest for %d seconds...' % (command_interval))
        st = time.time()
        while time.time() - st < command_interval:
            time.sleep(1)
            ret += self.read_output()
        # time.sleep(command_interval)
        ret += self.read_output()
        return ret.upper()

    def load_sef(self):
        self.logger.info('Start load sef file ...')
        sef = self.artiza.sef_filename
        self.logger.info('Real Load: '+sef)
        self.execute_sm_command_and_wait_until_done('sef -f %s' % (sef), self.timer)
        self.logger.info('Start load sef file Done')

    def start_module(self):
        self.logger.info('Start Module ...')
        self.execute_sm_command_and_wait_until_done('module -a start', 480)
        self.logger.info('Start Module Done')

    def stop_module(self, ignore_error=False):
        self.logger.info('Stop Module ...')
        self.execute_sm_command_and_wait_until_done('module -a stop', self.timer, ignore_error=ignore_error)
        self.logger.info('Stop Module Done')

    def start_interface(self):
        self.logger.info('Start Interface ...')
        self.execute_sm_command_and_wait_until_done('link -a up', self.timer)
        self.logger.info('Start Interface Done')

    def stop_interface(self, ignore_error=False):
        self.logger.info('Stop Interface ...')
        self.execute_sm_command_and_wait_until_done('link -a down', self.timer, ignore_error=ignore_error)
        self.logger.info('Stop Interface Done')

    def clear_setting(self, ignore_error=False):
        self.logger.info('Clear Setting ...')
        self.execute_sm_command_and_wait_until_done('set -a reset', self.timer, ignore_error=ignore_error)
        self.logger.info('Clear Setting Done')

    def load_setting(self):
        self.logger.info('Load Setting ...')
        self.execute_sm_command_and_wait_until_done('set -a load',  self.timer)
        self.logger.info('Load Setting Done')

    def start_sim(self, seq_list):  # seq_list is a string, like: seq1,seq1,seq3
        self.logger.info('Start Sim of %s...' % (str(seq_list)))
        self.execute_sm_command_and_wait_until_done('sim -a start -g %s' % (seq_list),  self.timer)
        self.logger.info('Start Sim Done')

    def stop_sim(self, ignore_error=False):
        self.logger.info('Stop Simulator ...')
        self.execute_sm_command_and_wait_until_done('sim -a stop',  self.timer, ignore_error=ignore_error)
        self.logger.info('Stop Sim Done')

    def start_burst(self, seq_list, call, interval, loopcount):
        self.logger.info('Start Burst of %s...' % (str(seq_list)))
        self.execute_sm_command_and_wait_until_done(command='burst -a start -g %s -c %s -i %s -l %s' % (seq_list,
                                                                                                        call, interval, loopcount
                                                                                                        ),  command_interval=10)
        self.logger.info('Start Burst Done')

    def stop_burst(self, seq_list):
        self.logger.info('Stop Burst of %s...' % (str(seq_list)))
        self.execute_sm_command_and_wait_until_done('burst -a stop', self.timer, ignore_error=ignore_error)
        self.logger.info('Stop Burst Done')

    def close_sef(self, ignore_error=False):
        self.logger.info('Close sef ...')
        self.execute_sm_command_and_wait_until_done('close',  self.timer, ignore_error=ignore_error)
        self.logger.info('Close sef Done')

    def cell_search(self):
        self.logger.info('Cell Searching ...')
        self.execute_sm_command_and_wait_until_done('cellsearch',  self.timer)
        self.logger.info('Cell Searching Done')

    def get_cplan_statistic(self):  # export to csv file, and then parse it
        timestamp = time.strftime("%Y_%m_%d__%H_%M_%S")
        filename = r'%s\cplan_%s.txt' % (self.artiza.config.taserver_workspace, timestamp)
        cmd = 'textout -s cstatlist -o txt -f %s' % (filename)
        self.execute_sm_command_and_wait_until_done(cmd,  self.timer, True)

        filename = '%s/cplan_%s.txt' % (gv.artiza.config.taserver_local_workspce, timestamp)
        lines = open(filename).readlines()
        lines = [line for line in lines if 'seq'.upper() in line.upper()]
        fields = [x.lower().replace(' ', '_')
                  for x in lines[0].replace('#', '').replace('Target No', 'cell').split(',')]
        result = []
        for line in lines[1:]:
            item = IpaMmlItem()
            values = line.lower().replace(' ', '_').split(',')
            for fieldname in ['seq', 'cell', 'seq_start', 'seq_comp', 'seq_incomp', 'seq_release', 'seq_comp_rate']:
                index = fields.index(fieldname)
                value = values[index]
                value = value.replace('seq.', '') if fieldname == 'seq' else value
                value = value.replace('node_', '').replace('cell', '') if fieldname == 'cell' else value
                setattr(item, fieldname, value)
            result.append(item)
        self.stat_result.cplan_history.append(result)
        return result

    def get_tput_stat(self):
        for stat_type in ['macstatlist']:
            timestamp = time.strftime("%Y_%m_%d__%H_%M_%S")
            filename = r'%s\%s_%s.csv' % (self.artiza.config.taserver_workspace,
                                          stat_type.replace('statlist', ''), timestamp)
            cmd = 'textout -s %s -o csv -f %s' % (stat_type, filename)
            self.execute_sm_command_and_wait_until_done(cmd,  self.timer, True, 10)

    def restart_all_module_except_cpu(self):
        self.logger.info('Restart Box ...')
        self.execute_sm_command_and_wait_until_done('box -a restart',  600)
        self.logger.info('Resart Box Done')

    def setup_before_bts_onair(self):
        if self.is_running():
            self.logger.info('System Manager is Running')
            if not self.is_servermode():
                raise Exception, 'System Manager is running and is not Server Mode, TA will stop!!'
        else:
            self.logger.info('System Manager is not Running')
            self.start_app()

        # try to clean up environment again
        self.logger.info('Try to clean environment first.')
        self.stop_sim(ignore_error=True)
        # self.stop_burst(ignore_error = True)
        self.clear_setting(ignore_error=True)
        self.stop_interface(ignore_error=True)
        self.stop_module(ignore_error=True)
        self.close_sef(ignore_error=True)

        # prepare for this time running
        self.load_sef()
        self.restart_all_module_except_cpu()
        self.start_module()
        self.start_interface()
        self.load_setting()

    def setup_after_bts_onair(self):
        self.logger.info('Waiting for cell search...')
        time.sleep(180)
        self.cell_search()
        pass

    def setup(self):
        self.setup_before_bts_onair()

    def teardown(self):
        self.stop_sim(ignore_error=True)
        # self.stop_burst(ignore_error = True)
        self.clear_setting(ignore_error=True)
        self.stop_interface(ignore_error=True)
        self.stop_module(ignore_error=True)
        self.close_sef(ignore_error=True)


class c_pet_artiza(object):

    def __init__(self, id, logger):
        self.id = id
        self.config = self.read_config()
        self.conn_cpc = None
        self.sm_logfile = ''
        self.sef_filename = ''
        self.case = None
        self.raw_sef = False
        self.sef = None
        self.logger = logger

        self.sm = c_pet_system_manager(self)

    def set_case(self, case):
        self.case = case
        if ':' in case.prf_sef_path:
            self.logger.info('Use Raw SEF')
            self.sef_filename = '"%s"' % (case.prf_sef_path)
            self.raw_sef = True
        else:
            self.sef_filename = os.sep.join([os.path.sep.join([resource_path(), 'config', 'artiza', 'artiza_%s' % (self.id)]),
                                             case.prf_sef_path.replace('\\', '/')])
        self.sef_filename = '"%s"' % (self.sef_filename.replace('"', ''))
        self.logger.info('SEF Path: ' + self.sef_filename)
        if not self.raw_sef:
            self.sef = c_pet_sef(self.sef_filename)
            self.sef.case = case

    def read_config(self):
        artizapath = os.path.sep.join([resource_path(), 'config', 'artiza', 'artiza_%s' % (self.id)])
        import sys
        import importlib
        sys.path.append(artizapath)
        model = importlib.import_module('artiza_%s' % (self.id))
        artizaconfig = IpaMmlItem()
        for key in model.TOOLS_VAR:
            setattr(artizaconfig, key.lower(), model.TOOLS_VAR[key])
        return artizaconfig

    def connect_to_cpc(self):
        if not self.conn_cpc:
            self.conn_cpc = connections.connect_to_host(self.config.cpc_ip,
                                                        self.config.cpc_port,
                                                        self.config.cpc_username,
                                                        self.config.cpc_password)
        connections.switch_host_connection(self.conn_cpc)

    def disconnect_cpc(self):
        if self.conn_cpc:
            connections.switch_host_connection(self.conn_cpc)
            connections.disconnect_from_host()
            self.conn_cpc = None

    def execute_command_on_cpc(self, command):
        self.connect_to_cpc()
        return connections.execute_shell_command_without_check(command)

    def set_sm_logfile(self, filename):
        self.sm.set_logfile(filename)

    def setup(self):
        if self.sef:
            self.sef.setup()
        self.sm.setup()
        if self.config.taserver_local_workspce:
            os.system('rm -rf %s/*.*' % (self.config.taserver_local_workspce))

    def teardown(self):
        # self.sm.teardown()
        self.disconnect_cpc()


class c_pet_sef(object):

    def __init__(self, filename):
        self.sef_file = filename
        self.file_index = 0
        self.dst_dire = ''
        self.file_map = {}
        self.real_sef = ''
        self.spf = None
        self.logger = None

    def prepare_dst_dire(self):
        self.dst_dire = case_file('artiza/script')
        if self.dst_dire:
            if os.path.exists(self.dst_dire):
                run_local_command('rm -rf ' + self.dst_dire)
            run_local_command('mkdir ' + self.dst_dire)
        else:
            raise Exception, 'Please specific the destination file directory first.'

    def deal_with_file(self, filename='', mode='Normal'):
        if mode == 'CFG':
            sdl_file = filename.replace('.cfg', '.sdl')
            sdl_dst = self.file_map[sdl_file]
            cfg_src = filename.replace('\\', '/')
            cfg_dst = sdl_dst.replace('.sdl', '.cfg')
            dst_filename = os.sep.join([self.dst_dire, cfg_dst])
            run_local_command('cp "%s" %s' % (cfg_src.replace('"', ''), dst_filename))
            self.file_map[filename] = os.path.basename(dst_filename)
            return dst_filename
        else:
            if filename in self.file_map:
                self.logger.info('File already prcessed, [%s]' % (filename))
                return self.file_map[filename]
            else:
                newfilename = filename.replace('\\', os.sep).replace('"', '')
                if not os.path.exists(newfilename):
                    self.logger.warning('Warning: File not exist [%s]' % (newfilename))
                    return None
                dst_filename = ('%0.4d%s' % (self.file_index, os.path.splitext(newfilename)[-1])).replace('"', '')
                dst_filename = os.sep.join([self.dst_dire, dst_filename])
                run_local_command('cp "%s" %s' % (newfilename.replace('"', ''), dst_filename))
                self.file_map[filename] = os.path.basename(dst_filename)
                self.file_index += 1
                return dst_filename

    def setup(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        self.prepare_dst_dire()
        self.file_index = 0
        dsef = self.deal_with_file(self.sef_file)
        if not dsef:
            raise Exception, 'SEF file does not exist'
        filelist = []
        from lxml import etree
        tree = etree.parse(dsef)
        simulators = tree.xpath('//simulator')
        for simulator in simulators:
            config = simulator.get('configfile')
            if config:
                filelist.append(config)
        for spf in tree.xpath('//spf'):
            filelist.append(spf.text)
        self.real_sef = dsef
        lines = open(dsef).read()
        for inline_filename_o in filelist:
            inline_filename = os.sep.join([os.path.dirname(self.sef_file), inline_filename_o])
            dst_filename = self.deal_with_file(inline_filename)
            if dst_filename:
                lines = lines.replace(inline_filename_o, '.\\' + os.path.basename(dst_filename))
        with open(dsef, 'w') as f:
            f.write(lines)

        self.explore_spf(inline_filename, dst_filename)
        self.save_file_map()

        self.spf = c_pet_spf(self.spf_file, self.case)
        self.spf.sef = self
        self.spf.setup()

    def save_file_map(self):
        with open(os.sep.join([self.dst_dire, 'file_map.txt']), 'a') as f:
            files = self.file_map.values()
            files.sort()
            for filename in files:
                src_filename = [x for x in self.file_map if self.file_map[x] == filename][0].split('/')[-1]
                f.write('%s             %s \n' % (filename, src_filename))

    def explore_spf(self, src_spf, dst_spf):
        self.logger.info('Processing SPF File...................')
        file_ext_list = ['.xml', '.sdl', '.cfg', '.pdm', '.txt', '.csv']
        src_spf = src_spf.replace('"', '')
        parent_dire = os.path.abspath(os.path.dirname(src_spf.replace('\\', '/')))
        lines = open(dst_spf).read().splitlines()
        filelist = []
        spf = []
        for line in lines:
            for ext in file_ext_list:
                if ext.upper() in line.upper():
                    inline_name = line.split('>')[1].split('<')[0]
                    filelist.append(inline_name)
                    break

        lines = open(dst_spf).read()
        for filename in filelist:
            real_file = os.path.abspath(os.sep.join([parent_dire, filename]))
            dst_file = self.deal_with_file(real_file)
            if dst_file:
                lines = lines.replace(filename, '.\\'+os.path.basename(dst_file))
                if os.path.splitext(dst_file)[-1] == '.sdl':
                    self.explore_sdl(real_file, dst_file)
            else:
                lines = lines.replace(filename, '')
        with open(dst_spf, 'w') as f:
            f.write(lines)
        self.spf_file = dst_spf

    def explore_sdl(self, src_sdl, dst_sdl):
        self.logger.info('Processing SDL File...................')
        parent_dire = os.path.dirname(src_sdl.replace('\\', '/').replace('"', ''))

        cfgfile = src_sdl.replace('.sdl', '.cfg')
        if cfgfile not in self.file_map:
            dst_cfg = self.deal_with_file(cfgfile, 'CFG')
            lines = open(dst_cfg).read().splitlines()
            newcfg = []
            for line in lines:
                pdm = ' '.join(line.split()[1:])
                index = line.split()[0]
                pdm_full = os.sep.join([parent_dire, pdm])
                dst_pdm = self.deal_with_file(pdm_full)

                newcfg.append('%s%s.\\%s' % (index, chr(9), os.path.basename(dst_pdm)))
            with open(dst_cfg, 'w') as f:
                for line in newcfg:
                    f.write(line+'\n')


class c_pet_spf(object):

    def __init__(self, filename, case):
        self.filename = filename
        from lxml import etree
        self.tree = etree.parse(self.filename)
        self.sef = None
        self.case = case
        self.logger = None

    def modifynode(self, node, value):
        value = None if value == '' else value
        if node is not None:
            if node.text is not None or value is not None:
                if node.text <> value:
                    self.logger.info('Modify SPF: [%s], oldvalue: [%s], New value: [%s]' %
                                     (node.getroottree().getpath(node), node.text, value))
                    node.text = value

    def adapt_cells(self, cell_list=['1']):
        cells = self.tree.xpath('/spf/system/simulator[descendant::valid[text()="true"]]')
        for cell in cells:
            cellid = cell.get('name').upper().replace('CELL', '')
            if not cellid in cell_list:
                valid = cell.xpath('./valid')[0]
                self.modifynode(valid, 'false')
                # valid.text = 'false'
        sdlgens = self.tree.xpath('/spf/sdl_table/gen')
        for gen in [x for x in sdlgens if 'Gen.' in x.get('name')]:
            seqid = gen.get('name').upper().replace('GEN.', '').strip()
            if seqid not in cell_list:
                for sdl in gen.xpath('./sdl'):
                    self.modifynode(sdl.xpath('./primary')[0], '')
                    self.modifynode(sdl.xpath('./secondary')[0], '')
                self.modifynode(gen.xpath('./gen_table')[0], '')
                self.modifynode(gen.xpath('./rrc_table')[0], '')

        trigger_settings = self.tree.xpath('/spf/trigger/settings')
        default_setting = [x for x in trigger_settings if x.get('name') == 'All'][0]
        gens = default_setting.xpath('./gen')

        for gen in gens:
            if 'GEN.' in gen.get('name').upper():
                if gen.get('name').upper().replace('GEN.', '') in cell_list:
                    self.modifynode(gen.xpath('./reg')[0], 'true')
                else:
                    self.modifynode(gen.xpath('./reg')[0], 'false')
        self.tree.write(self.filename, xml_declaration=True, encoding='UTF-8')

    def adapt_parameter_with_case(self):
        trigger_settings = self.tree.xpath('/spf/trigger/settings')
        default_setting = [x for x in trigger_settings if x.get('name') == 'All'][0]
        gens = default_setting.xpath('./gen')
        for gen in gens:
            if self.case.prf_case_type.upper() in ['Attach&Deattach'.upper(), 'Paging'.upper(), 'DRB']:
                if gen.get('id') in ['4', '5', '6']:
                    self.modifynode(gen.xpath('./value')[0], str(int(self.case.prf_caps)*60))
                    self.modifynode(gen.xpath('./stop_call_count')[0], str(int(self.case.prf_caps)*3600))
            if self.case.prf_case_type.upper() in ['Handover'.upper()]:
                self.case.prf_hi_caps = self.case.prf_caps.replace(';', ',').split(',')[0]
                self.case.prf_ho_caps = self.case.prf_caps.replace(';', ',').split(',')[1]
                if gen.get('id') in ['4', '6', '8']:
                    self.modifynode(gen.xpath('./value')[0], str(int(self.case.prf_ho_caps)*60))
                    self.modifynode(gen.xpath('./stop_call_count')[0], str(int(self.case.prf_ho_caps)*3600))
                if gen.get('id') in ['5', '7', '9']:
                    self.modifynode(gen.xpath('./value')[0], str(int(self.case.prf_hi_caps)*60))
                    self.modifynode(gen.xpath('./stop_call_count')[0], str(int(self.case.prf_hi_caps)*3600))
        self.tree.write(self.filename, xml_declaration=True, encoding='UTF-8')

    def setup(self):
        self.adapt_cells(self.case.prf_used_cells.split(','))
        self.adapt_parameter_with_case()
        self.adapt_sdl_with_case()
        pass

    def adapt_sdl_with_case(self):
        sdl_seq1 = self.tree.xpath('/spf/sdl_table/gen[@name="Gen.1"]')[0]
        sdls = sdl_seq1.xpath('./sdl[@name="S1AP"]') + sdl_seq1.xpath('./sdl[@name="RRC"]')
        msgid = ''
        if self.case.prf_case_type.upper() in ['Attach&Deattach'.upper(), 'Paging'.upper()]:
            msgid = '200000'
        if msgid:
            for primary_node in [x.xpath('./primary')[0] for x in sdls]:
                filename = os.sep.join([self.sef.dst_dire, os.path.basename(primary_node.text).replace('.\\', '')])
                self.logger.info('Adapt SDL file: ' + filename)
                result = []
                for line in open(filename).read().splitlines():
                    if line.startswith(msgid):
                        if len(line.split()) == 2:
                            newline = '%s%s%s' % (msgid, chr(9), self.case.prf_wait_timer)
                            self.logger.info('SDL Changing: [%s] -> [%s]' % (line, newline))
                            result.append(newline)
                        else:
                            result.append(line)
                    else:
                        result.append(line)

                with open(filename, 'w') as f:
                    for line in result:
                        f.write(line + '\n')


def parse_cplan_stat(filename):
    lines = open(filename).readlines()
    lines = [line for line in lines if 'seq'.upper() in line.upper()]
    fields = [x.lower().replace(' ', '_') for x in lines[0].replace('#', '').replace('Target No', 'cell').split(',')]
    result = []
    for line in lines[1:]:
        item = IpaMmlItem()
        values = line.lower().replace(' ', '_').split(',')
        for fieldname in ['seq', 'cell', 'seq_start', 'seq_comp', 'seq_incomp', 'seq_release', 'seq_comp_rate']:
            index = fields.index(fieldname)
            value = values[index]
            value = value.replace('seq.', '') if fieldname == 'seq' else value
            value = value.replace('node_', '').replace('cell', '') if fieldname == 'cell' else value
            setattr(item, fieldname, value)
        result.append(item)
    return result


def get_cplan_item(cell, seq, data):
    return [x for x in data if str(x.cell) == str(cell) and str(x.seq) == str(seq)][0]


if __name__ == '__main__':
    data = parse_cplan_stat('/home/work/mnt/buf134/cplan_2017_06_01__15_21_57.txt')
    amap = [[u'1', u'1'], [u'1', u'4'], [u'1', u'7'], [u'1', u'10'], [u'2', u'2'], [u'2', u'5'],
            [u'2', u'8'], [u'2', u'11'], [u'3', u'3'], [u'3', u'6'], [u'3', u'9'], [u'3', u'12']]
    for line in amap:
        cell, seq = line
        line_cell = get_cplan_item(cell, seq, data)
        print line_cell
    print len(data)

    # artiza = c_pet_artiza(124)

    # a = c_pet_artiza(124)
    # sm = a.sm
    # sm.connect()

    # print artiza.config
    # artiza.setup()
    # artiza.teardown()

    # sef = '"/home/work/tacase/Resource/config/artiza/artiza_124/script/01_attach_detach_3cell_good/New Test Case/Attach_detach_20MHz_Supercell_FSIH_FZND.sef"'
    # # sef = '"/home/work/tacase/Resource/config/artiza/artiza_124/script/01_attach_detach_3cell_good/New Test Case/ta.sef"'
    # sef =  "/home/work/tacase/Resource/config/artiza/artiza_124/cxd/01_attach_detach_3cell_good/New Test Case/Attach_detach_20MHz_Supercell_FSIH_FZND.sef"
    # sef =  "/home/work/tacase/Resource/config/artiza/artiza_124/jufei/01_attach_detach_3cell_good/New Test Case/Attach_detach_20MHz_Supercell_FSIH_FZND.sef"
    # spf = c_pet_spf(sef)
    # # spf.dst_dire = '/home/work/jrun/TL17SP_CAP_00252_20M_ULDL1_SSF7_TM3_PRF__2017_02_28__10_22_12/NORMAL_NO1/aritza/script/'
    # spf.dst_dire =  '/home/work/temp/2'

    # spf.setup()
    # # spf.get_related_filelist2()

    # spf = c_pet_spf('/home/work/tacase/temp/0002.spf')
    # spf.adapt_cells(['1'])
    # spf.adapt_sdl_with_case(None)
