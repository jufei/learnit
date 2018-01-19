import os, time, sys
from petbase import *
from optparse import *

from pet_bts import read_bts_config
from pettool import get_case_config_new
from petcasebase import re_organize_case
from pet_bts import pet_bts_read_scf_file, prepare_mr_parameters
from PetShell.file_lib.xml_control import common_xml_operation, ParseXML
from pet_scf_manager import pet_scf_manager

class c_scf_debug(object):
    def __init__(self):
        self.env = IpaMmlItem()
        self.read_env_variables()

        print self.env
        self.btsid      = self.env.btsid.upper().replace('BTS', '')
        self.caseid     = self.env.caseid
        self.case       = get_case_config_new(self.caseid)
        self.bts        = read_bts_config(self.btsid)

        gv.master_bts = self.bts
        gv.case.curr_case = self.case
        re_organize_case()
        pet_bts_read_scf_file(self.btsid)

    def read_env_variables(self):
        for key in os.environ.keys():
            setattr(self.env, key.lower().replace(' ','_'), os.environ[key])

        if hasattr(self.env, 'btsid'):
            return
        else:
            parser = OptionParser()
            parser.add_option("-b",  "--btsid", dest="btsid", default='1601', help='BTS ID')
            parser.add_option("-c",  "--caseid", dest="caseid", default='670000', help='BTS ID')
            (options, sys.argv[1:]) = parser.parse_args()
            self.env.btsid = options.btsid.upper().replace('BTS', '')
            self.env.caseid = options.caseid

    def gen_scf(self):
        if self.case.domain == 'MR':
            prepare_mr_parameters()

        scf_manager = pet_scf_manager(self.case, self.bts)
        changes = scf_manager.gene_change_list()

        accept_changes = [x for x in changes if not 'delete' in x]
        for change in [x for x in changes if 'delete' in x]:
            try:
                common_xml_operation(pathc(bts_source_file(self.btsid, self.case.scf_file)), '/tmp/dest_scf', [change])
                accept_changes.append(change)
            except:
                print 'Process  [%s] error' %(change)

        common_xml_operation(pathc(bts_source_file(self.btsid, self.case.scf_file)),
                '/home/work/temp/your_scf.xml', accept_changes)
        print 'Your SCF is here: http://10.69.2.134/job/113server/ws/home/work/temp/your_scf.xml'




def main(args = sys.argv[1:]):
    scf_debug = c_scf_debug()
    scf_debug.gen_scf()

if __name__ == '__main__':
    main()
