from petbase import *
from pet_scf_base_c import c_pet_scf_base, scf_parameters

fdd_scf_pms = {
    'dlChBw'                        :       'get_dlChBw',
}

fdd_tput_scf_params = [
        'actDrx',
        # 'actServiceAccountSsh',
        # 'actServicePortState',
        'actRLFReportEval',
        'actFastMimoSwitch',
        'actModulationSchemeUL',
        # 'actTmSwitch',
        'cellSrPeriod',
        'actProactSchedBySrb',
        'actRLFReportEval',
        'actAutoPucchAlloc',
        # 'actCellTrace',
        # 'actReduceWimaxInterference',
        # 'actUpPtsBlanking',
        'actULCAggr',
        'activatedMimoTM',
        'dlChBw',
        'cqiPerNp',
        'dlInterferenceSpatialMode',
        'dlMimoMode',
        'dlSectorBeamformingMode',
        'earfcn',
        'ethernetPortSecurityEnabled',
        'ilReacTimerUl',
        'inactivityTimer',
        'ipAddrPrim',
        'iniMcsUl',
        'maxNumUeDl',
        'maxNumUeUl',
        # 'maxNumUeDlDwPTS',
        'prachCS',
        'prachConfIndex',
        'prachFreqOff',
        'reportingIntervalPm',
        'riEnable',
        # 'rxCalibrationConfiguration',
        'sCellTmSettingWithBf',
        # 'srsOnTwoSymUpPts',
        # 'srsSubfrConf',  #Follow the template, not changed
        'subfrPShareRequired',  #mbms parameter
        'syncSigTxMode',
        # 'tddFrameConf',
        # 'tddSpecSubfConf',
        'riPerM',
        'riPerOffset',
        'maxNrSymPdcch',
        'n1PucchAn'
        # 'numOfCsiRsAntennaPorts',
]


from pet_xml import *

class c_pet_scf_c_fdd(c_pet_scf_base):
    def __init__(self, pmlist):
        self.pmlist = pmlist
        for pm in fdd_scf_pms:
            if not pm in scf_parameters.keys():
                scf_parameters[pm] = fdd_scf_pms[pm]


    def get_dlChBw(self, bts, case):
        result = []
        bandlist = case.band.upper().replace('M','').split('-')
        bandlist = bandlist * int(bts.cell_count/len(bandlist))
        values = [bandlist[cellid]+' MHz' for cellid in range(bts.cell_count)]
        return modify_parameter(bts, 'dlChBw', values)


    def get_earfcndl(self, bts, case):
        def is_slave_bts():
            return gv.slave_bts and bts.bts_id == gv.slave_bts.bts_id
        result = []
        values = []
        if case.domain == 'CPK' and bts.rru_type == 'FZHJ':
            band = bts.band.upper().replace('M','')
            if band == '10-20':
                values = ['38050', '37900']
            if band == '20-10':
                values = ['37900', '38050']
            if band == '20-20-10':
                values = ['40540', '49723', '40861']
            if band == '20-20-20':
                values = ['40540', '40740', '40938']
            if values:
                result = modify_parameter(bts, 'earfcndl', values)


        if case.domain == 'CPK' and case.ulca:
            band = case.band.upper().replace('M','')
            if band == '20-10':
                values = ['37900', '38050']
            if band == '20-20':
                values = ['37900', '38100']
            if values:
                result = modify_parameter(bts, 'earfcndl', values)
        for i in values:
            result += modify_parameter(bts, 'earfcnul', i+18000)

        if bts.new_earfcn_list:
             result += modify_parameter(bts, 'earfcndl', bts.new_earfcn_list)
        return result


