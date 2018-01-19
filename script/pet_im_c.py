from petbase import *
from ute_infomodel import ute_infomodel
import threading
from thread import *

def infomodel_monitor_thread(im):
    pet_bts_alarm_path = {
        'RL55' : ['/MRBTS-*/RAT-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'RL65' : ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'TL16' : ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'TL16A': ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
        'TL17' : ['/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/ALARM_L-*', '/MRBTS-*/RAT-*/BTS_L-*/LNBTS-*/LNCEL-*/ALARM_L-*'],
    }
    cellstr = im.get_cell_object_name()
    if not im.infomodel:
        return 0
    cell_count = len(im.infomodel.query_infomodel('get list %s' % (cellstr), alias = im.im_alias, timeout = 10))

    while True:
        if not gv:
            return 0
        if gv.case.done:
            return 0
        if gv.case.start_testing:
            for i in range(cell_count):
                if im.bts.sw_release == 'RL55':
                    cellstr = '/MRBTS-1/RAT-1/BBTOP_L-1/LCELL-%d' % (i + 1)
                else:
                    cellstr = '/MRBTS-1/RAT-1/BTS_L-1/BBTOP_L-1/LCELL-%d' % (i + 1)

                mo = None
                if im.infomodel:
                    try:
                        mo = im.infomodel.get_infomodel_object(cellstr, timeout = 5, alias = im.im_alias)
                        state = mo['stateInfo']['proceduralState']
                    except:
                        pass

                    error_msg = ''
                    if mo <> None:
                        if state.upper().strip() <> 'onAirDone'.upper():
                            error_msg = 'CELL %d is not onAir, it is: %s.' % (i + 1, state)

                    if error_msg <> '':
                        gv.suite.health = False
                        gv.case.monitor_error_msg = error_msg
                        return 0

        time.sleep(3)


class c_pet_im(object):
    def __init__(self, bts, working_dire):
        self.bts = bts
        self.working_dire = working_dire

    def get_cell_object_name(self):
        if self.bts.config.sw_release == 'RL55':
            return '/MRBTS-1/RAT-1/BBTOP_L-1/LCELL-*'
        elif self.bts.config.sw_release == 'RL65':
            return '/MRBTS-1/RAT-1/BTS_L-1/BBTOP_L-1/LCELL-*'
        else:
            return '/MRBTS-1/RAT-1/BTS_L-1/LNBTS-1/LCELL-*'


    def setup(self):
        if not self.bts:
            raise Exception, 'Attach a bts first.'
        def get_infomodel_pid():
            return [x.split()[1] for x in os.popen('ps -ef|grep java|grep %s_' %(self.bts.btsid)).readlines()]
        run_local_command('ps -ef|grep name')
        path = self.working_dire
        remote_path = '/ffs/run/swpool/OAM/meta_*.zip' if self.bts.config.airscale else '/ffs/run/meta_*.zip'
        filename = [x for x in self.bts.execute_command_local('ls -la ' + remote_path) if 'meta_' in x][0].split()[-1]
        self.bts.download_file(path + filename.split('/')[-1], filename.split('/')[-1], '/'.join(filename.split('/')[:-1]))
        self.infomodel_lock = threading.Lock()
        connected = False
        for pid in get_infomodel_pid():
            from pettool import pet_process_exist
            if pet_process_exist(pid):
                run_local_command('kill -9 ' + pid)
        try:
            with self.infomodel_lock:
                self.infomodel = ute_infomodel()
                self.im_alias = self.bts.btsid + time.strftime("_%Y_%m_%d__%H_%M_%S")
                self.infomodel.setup_infomodel(address = self.bts.config.bts_control_pc_lab, port = 12345,
                                definitions_file_path = path + filename.split('/')[-1], alias = self.im_alias)
                for i in range(24):
                    try:
                        self.infomodel.connect_infomodel(alias = self.im_alias)
                        connected = True
                        break
                    except:
                        self.logger.info('Connect to infomodel failed, I will try later!')
                        time.sleep(5)
                if not connected:
                    raise Exception, 'Could not connect infomodel successfully in 2 minutes'
                self.infomodel.start_infomodel_logger(alias = self.im_alias)
        finally:
            self.infomodel_pid = get_infomodel_pid()
        run_local_command('ps -ef|grep name')

    def teardown(self):
        run_local_command('ps -ef|grep name')
        if self.infomodel:
            oldmodel = self.infomodel
            self.infomodel = None
            try:
                try:
                    oldmodel.save_infomodel_log(os.sep.join([self.working_dire,
                        'infomodel_%s_%s' % (self.bts.btsid, time.strftime("%Y_%m_%d__%H_%M_%S"))]), alias = self.im_alias)
                finally:
                    oldmodel.teardown_infomodel(alias = self.im_alias)
            finally:
                from pettool import pet_process_exist
                for pid in self.infomodel_pid:
                    if pet_process_exist(pid):
                        run_local_command('kill -9 ' + pid)
        run_local_command('ps -ef|grep name')

    def start_monitor(self):
        start_new_thread(infomodel_monitor_thread , (self,))

    def stop_monitor(self):
        self.teardown()