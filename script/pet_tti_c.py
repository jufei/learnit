import os,time
from petbase import *
#from pet_bts import *

class c_tti_trace(object):
    def __init__(self, bts_control_pc_lab_ip, bts_sw_release, bts_cell_count, bts_version, tti_tool_path, save_log_path, duration_time):

        self.telnet_ip      = bts_control_pc_lab_ip
        self.sw_release     = bts_sw_release
        self.cell_count     = bts_cell_count
        self.bts_version    = bts_version
        self.save_log_path  = save_log_path
        self.core_info      = ''
        self.tti_tool_path  = tti_tool_path
        self.stream      = None
        self.ttiparser      = ''
        self.duration_time  = duration_time


    def get_tti_core_info(self):
        if self.sw_release == 'RL55':
            self.core_info = '1231,1234'
            return
        if self.sw_release in ['RL65', 'TL15A', 'TL16', 'TL16A'] and self.cell_count == 1:
            self.core_info = '1232,1233'
            return
        # if self.sw_release in ['TL16', 'TL16A', 'TL17'] and self.cell_count > 1:
        from pettool import execute_command_on_telnet
        output = execute_command_on_telnet(self.telnet_ip, '15007','getCellMapping @RROMexe', 0.5)
        title = [x for x in output.splitlines() if 'MACULTTI' in x][0]
        p1, p2 = title.find('MACULTTI'), title.find('MACDLTTI')
        cores = ','.join(['%s,%s' %(line[p1:p1 + 6], line[p2:p2 + 6])  for line in output.splitlines() if '0x1' in line])
        self.core_info = cores.replace('0x', '')
        print self.core_info

    def get_tti_application(self):
        if os.path.exists(os.sep.join([self.tti_tool_path, self.bts_version])):
            print self.bts_version
            gv.logger.info(self.bts_version)
            ttipath = os.sep.join([self.tti_tool_path, self.bts_version])

        else:
            print self.bts_version
            gv.logger.info(self.bts_version)
            version_prefix = self.bts_version.split('_')[0]
            dirlist = [dirname for dirname in os.listdir(self.tti_tool_path) if version_prefix in dirname]
            if len(dirlist) == 0:
                gv.logger.info('Could not find available ttiTrace tool')
            dirlist.sort()
            ttipath = os.sep.join([self.tti_tool_path, dirlist[-1]])
        self.stream = os.sep.join([ttipath, 'sicftp'])
        self.ttiparser = os.sep.join([ttipath, 'DevC_tti_trace_parser_64'])
        logdir = os.sep.join([self.save_log_path, 'TtiTrace'])
        os.system('chmod +x ' + self.stream)
        os.system('chmod +x ' + self.ttiparser)

    def start_capture_tti_log(self):
        logdir = os.sep.join([self.save_log_path, 'TtiTrace'])
        cmd = str(' '.join([self.stream, '-c', self.core_info, '-q', '-n', self.telnet_ip, '-o', logdir]))
        run_local_command_gracely(cmd)
        # self._stop_and_decode_tti_log()

    def _stop_and_decode_tti_log(self):
        filelist = os.listdir(self.save_log_path)
        allfiles = [filename for filename in filelist if '.dat' in filename]
        if len(allfiles) == 0:
            for filename in filelist:
                print filename
            print 'Cound not find the tti trace file, please check it.'
        for logfile in allfiles:
            parsed_filname = logfile.split('.')[0]+'.csv'
            parsed_firdir = os.sep.join([self.save_log_path, parsed_filname])
            run_local_command('%s %s %s' %(self.ttiparser, os.sep.join([self.save_log_path, logfile]), parsed_firdir))

    def remove_all_log(self):
        import os
        if os.path.exists('%s/dldata.csv' %(self.save_log_path)):
            os.remove('%s/dldata.csv' %(self.save_log_path))
        if os.path.exists('%s/uldata.csv' %(self.save_log_path)):
            os.remove('%s/uldata.csv' %(self.save_log_path))



    def prepare_all_tti_trace_data(self):
        uldata = {}
        for line in open('%s/uldata.csv' %(self.save_log_path)).readlines()[2:]:
            if line.split(',')[2].strip() == '-' or line.split(',')[17].strip() == '-' or line.split(',')[-4].strip() == '-':
                continue
            adata = IpaMmlItem()
            if line.split(',')[1] <> '-':
                adata.esfn = int(line.split(',')[2].strip())
                adata.user = int(line.split(',')[14].strip())
                uldata[str(len(uldata))] = adata

    def parse_csv_file(self):
        pass


    def check_tti_trace_kpi(kpi_name, formula):
        pass


if __name__ == '__main__':

    from pet_bts import read_bts_config, execute_simple_command_on_bts
    bts = read_bts_config('1412')
    print bts
    # output = execute_simple_command_on_bts('1412', 'ls /ffs/run/Target*.xml')
    # line = [x for x in output if '.xml' in x][0]
    # bts.bts_version =  '_'.join(line.split('/')[-1].split('.xml')[0].split('_')[1:])
    # # bts.read_config()
    # bts.get_bts_version()


    tti_tool_path = '/data/pylib/tools/ttitrace'
    save_log_path = '/tmp'

    #temp = c_tti_trace(bts.config.bts_control_pc_lab, bts.config.sw_release, bts.config.cell_count, bts.bts_version, tti_tool_path, save_log_path)
    temp = c_tti_trace(bts.bts_control_pc_lab, bts.sw_release, '2', gv.env.bts_version, tti_tool_path, save_log_path, '60')

    temp._get_tti_core_info()
    temp._start_capture_tti_log()
    #temp.capture_tti_log_continously()
    #time.sleep(30)
    #temp._stop_and_decode_tti_log()

