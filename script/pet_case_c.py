from petbase import *
import logging
import datetime

class c_pet_case(IpaMmlItem):
    def __init__(self, id):
        self.id = id
        self.logger = logging.getLogger(__file__)
        self.read_case_config()

    def _get_db_file(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        return os.sep.join(curr_path.split(os.sep) + ['config', 'case', 'database.xlsx'])

    def read_case_config(self):
        from pet_db import read_all_case_db
        acase = None
        all_case = read_all_case_db()
        acase = [x for x in all_case if x.qc_test_instance_id == self.id]
        if acase:
            acase = acase[0]
            self.logger.info('Found case in DB.')
        else:
            from petbase import read_excel_sheet
            allcase = read_excel_sheet(self._get_db_file(), 'cases')
            acase = [case for case in allcase if int(case.qc_test_instance_id) == int(self.id)]
            if acase:
                acase = acase[0]
                self.logger.info('Found case in Excel.')
        if not acase:
            raise Exception, 'Could not find the case for qc_test_instance_id: [%s], please check it.' %(self.id)

        for attr in [x for x in dir(acase) if x[0] <> '_']:
            setattr(self, attr, getattr(acase, attr))
        self.re_organize_case_info()

    def re_organize_case_info(self):
        init_data = {
             'format'                       :   '0',
             'ho_type'                      :   '',
             'mr_paging_ue_count'           :   '0',
             'mr_paging_impair_ue_count'    :   '0',
             'mr_call_drop_ue_count'        :   '0',
             'mr_cd_impair_ue_count'        :   '0',
             'mr_intra_ho_ue_count'         :   '0',
             'mr_ho_impair_ue_count'        :   '0',
             'mr_volte_ue_count'            :   '0',
             'mr_volte_impair_ue_count'     :   '0',
             'mr_volte_ho_ue_count'         :   '0',
             'mr_volte_ho_impair_ue_count'  :   '0',
             'ho_stagger'                   :   '25',
             'cd_stagger'                   :   '25',
             'mr_volte_ho_stagger'          :   '25',
             'paging_stagger'               :   '25',
             'mr_volte_stagger'             :   '25',
             'ca_type'                      :   '',
             'sector_start'                 :   '0',
             'sector_end'                   :   '360',
             'ref_signal_power'             :   '10',
             'cell_range'                   :   '1000',
             'format'                       :   '0',
             'ql'                           :   '5',
             'case_duration'                :   '3600',
             'tm500_version'                :   'L',
             'tm500_attach_file'            :   '',
        }
        case = self
        for attr in init_data:
            if hasattr(case, attr):
                if getattr(case, attr).strip() == '':
                    setattr(case, attr, init_data[attr])
                if getattr(case, attr).strip().endswith('.0') or\
                     attr in ['format', 'uldl', 'ssf', 'tm', 'pipe', 'band']:
                    setattr(case, attr, getattr(case, attr).strip()[:-2])
            else:
                setattr(case, attr, init_data[attr])
        for attr in ['ho_path', 'ho_type']:
            if hasattr(case, attr):
                if getattr(case, attr).strip() == '':
                    setattr(case, attr, getattr(case, attr))
        case.real_ue_count = case.ue_count
        case.real_paging_ue_count = int(case.mr_paging_ue_count) +\
                                    int(case.mr_paging_impair_ue_count)
        case.real_cd_ue_count = int(case.mr_call_drop_ue_count) +\
                                    int(case.mr_cd_impair_ue_count)
        case.real_ho_ue_count = int(case.mr_intra_ho_ue_count) +\
                                    int(case.mr_ho_impair_ue_count)
        case.real_volte_ue_count = int(case.mr_volte_ue_count) +\
                                     int(case.mr_volte_impair_ue_count) +\
                                     int(case.mr_volte_ho_ue_count) +\
                                     int(case.mr_volte_ho_impair_ue_count)
        case.real_call_drop_volte = int(case.mr_volte_ue_count) +\
                                     int(case.mr_volte_impair_ue_count)
        case.real_ho_volte = int(case.mr_volte_ho_ue_count) + int(case.mr_volte_ho_impair_ue_count)

        case.band = case.band.replace('M','')
        case.tm = case.tm.replace('TM','')
        case.is_handover = case.ho_type.strip() <> ''
        case.is_inter = case.ho_type == 'INTER'
        case.is_intra = case.ho_type == 'INTRA'
        case.is_sf = not case.different_frequency
        case.is_df = case.different_frequency
        # if str(case.different_frequency) in ['', 'Y', 'N']:
        #     case.is_sf = case.different_frequency <> 'Y'
        #     case.is_df = case.different_frequency == 'Y'
        # else:
        #     case.is_sf = int(case.different_frequency) <> 1
        #     case.is_df = int(case.different_frequency) == 1
        case.is_s1 = case.ho_path == 'S1'
        case.is_x2 = case.ho_path == 'X2'
        case.use_slave_bts = case.is_inter

        case.has_mr_volte = case.real_volte_ue_count >0
        case.has_impair =       int(case.mr_paging_impair_ue_count) +\
                                int(case.mr_cd_impair_ue_count) +\
                                int(case.mr_ho_impair_ue_count) +\
                                int(case.mr_volte_impair_ue_count) +\
                                int(case.mr_volte_ho_impair_ue_count) > 0
        case.has_ho_volte = case.real_ho_volte > 0

        if case.case_type.upper() == 'VOLTE_CALL_DROP':
            case.kpi += ';kpi_volte_call_drop_ratio:0'
        if case.case_type.upper() == 'VOLTE_CALL_SETUP':
            case.kpi += ';kpi_volte_call_setup_ratio:0'
        if case.case_type.upper() == 'VOLTE_CAP':
            case.kpi += ';kpi_volte_cap:%s' %(case.ue_count)
        if case.case_type.upper() == 'MIX_MR':
            case.kpi += ';kpi_cap:20;kpi_duration:%2.2f' %(int(case.case_duration)/60)
        if case.case_type.upper() == 'MIX_CAP'or case.team.upper() == 'PET2':
            case.kpi += ';kpi_cpuload:99'
        else：
            case.kpi += ';kpi_cpuload:70'

    def apply_case_to_bts_for_earfcn(self, master_bts = None, slave_bts = None):
        self.logger.info('Prepare earfcn for bts')
        case = self
        group_len = 2 if case.ca_type == '2CC' else 1
        group_len = 3 if case.ca_type == '3CC' else group_len
        reverse_f = [i + 1 for i in range(group_len)]
        if case.is_df:
            reverse_f = [2, 1] if group_len == 2 else [2]
            reverse_f = [2, 1, 3] if group_len == 3 else reverse_f

        cell_count = master_bts.scf.cell_count
        values = [0] * cell_count * 2 if case.is_inter else [0] * cell_count
        for i in range(group_len):
            values[i] = i + 1
            j = i + group_len
            j = j + cell_count if case.is_inter else j
            values[j] = reverse_f[i]
        earfcn_list = [node.text for node in master_bts.scf.looker.get_parameters('earfcn')]
        if case.is_inter:
            earfcn_list = earfcn_list + [node.text for node in slave_bts.scf.looker.get_parameters('earfcn')]

        for i in range(cell_count):
            earfcn_list[i] = master_bts.get_new_earfcn(i+1, values[i]) if values[i] <> 0 else earfcn_list[i]
            if case.is_inter:
                j = i + cell_count
                earfcn_list[j] = slave_bts.get_new_earfcn(i+1, values[j]) if values[j] <> 0 else earfcn_list[j]
        master_bts.new_earfcn_list = earfcn_list[:cell_count]
        if case.is_inter:
            slave_bts.new_earfcn_list = earfcn_list[cell_count:]

    def apply_case_to_bts_for_eutraCarrierInfo(self, master_bts = None, slave_bts = None):
        self.logger.info('Prepare eutraCarrierInfo for bts')
        case = self
        another_cell = 3 if case.ca_type == '2CC' else 2
        another_cell = 4 if case.ca_type == '3CC' else another_cell
        op_bts = master_bts if case.ho_type == 'INTRA' else slave_bts

        master_bts.new_eutraCarrierInfo_list = [0] * master_bts.scf.cell_count
        if slave_bts:
            slave_bts.new_eutraCarrierInfo_list = [0] * slave_bts.scf.cell_count

        master_bts.new_eutraCarrierInfo_list[0] = op_bts.new_earfcn_list[another_cell-1]
        op_bts.new_eutraCarrierInfo_list[another_cell-1] = master_bts.new_earfcn_list[0]

    def apply_case_to_bts_for_mr(self, master_bts = None, slave_bts = None):
        master_bts.parse_scf_file(master_bts.source_file(self.scf_file))
        self.apply_case_to_bts_for_earfcn(master_bts, slave_bts)
        self.apply_case_to_bts_for_eutraCarrierInfo(master_bts, slave_bts)

    def prepare_for_scf_genration(self, master_bts, slave_bts = None):
        master_bts.prepare_for_scf_generation()
        if slave_bts:
            slave_bts.prepare_for_scf_generation()
        if self.case_type == 'MIX_MR':
            if self.is_handover:
                self.apply_case_to_bts_for_earfcn(master_bts, slave_bts)
                if self.is_df:
                    self.apply_case_to_bts_for_eutraCarrierInfo(master_bts, slave_bts)



if __name__ == '__main__':
    case = c_pet_case('284230')
    print case