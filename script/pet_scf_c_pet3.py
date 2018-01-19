from petbase import *
from pet_scf_base_c import c_pet_scf_base, scf_parameters

tput_scf_params = [
        'actDrx',
        # 'actServiceAccountSsh',
        # 'actServicePortState',
        'actFastMimoSwitch',
        'actModulationSchemeUL',
        'actTmSwitch',
        'cellSrPeriod',
        'actReduceWimaxInterference',
        'actUpPtsBlanking',
        'actULCAggr',
        'activatedMimoTM',
        'chBw',
        'cqiPerNp',
        'dlInterferenceSpatialMode',
        'dlMimoMode',
        'dlSectorBeamformingMode',
        'earfcn',
        'ilReacTimerUl',
        'inactivityTimer',
        'ipAddrPrim',
        # 'maxNumRrc',
        'maxNumUeDlDwPTS',
        'prachCS',
        'prachConfIndex',
        'prachFreqOff',
        'reportingIntervalPm',
        'riEnable',
        'riPerM',
        'riPerOffset',
        'rxCalibrationConfiguration',
        'sCellTmSettingWithBf',
        'srsOnTwoSymUpPts',
        'srsSubfrConf',  #Follow the template, not changed
        'subfrPShareRequired',  #mbms parameter
        'syncSigTxMode',
        'tddFrameConf',
        'tddSpecSubfConf',
        # 'numOfCsiRsAntennaPorts',
]

pet3_scf_pms = {
}

from pet_xml import *

class c_pet_scf_c(c_pet_scf_base):
    def __init__(self, pmlist):
        self.pmlist = pmlist
        for pm in pet3_scf_pms:
            if not pm in scf_parameters.keys():
                scf_parameters[pm] = pet3_scf_pms[pm]

    def get_actCellTrace(self, bts, case):
        value = 'true' if case.f_678.strip() == 'Y' else 'false'
        return modify_parameter(bts, 'actCellTrace', value)

    def get_actMDTCellTrace(self, bts, case):
        value = 'true' if case.f_678.strip() == 'Y' else 'false'
        return modify_parameter(bts, 'actMDTCellTrace', value)

    def get_actRLFReportEval(self, bts, case):
        value = 'true' if case.f_678.strip() == 'Y' else 'false'
        return modify_parameter(bts, 'actRLFReportEval', value)

    def get_actMroInterRatUtran(self, bts, case):
        value = 'true' if case.f_1749 else 'false'
        return modify_parameter(bts, 'actMroInterRatUtran', value)

    def get_jobtype(self, bts, case):
        value = 'RLFReportsOnly' if case.f_678.strip() == 'Y' else 'TraceOnly'
        return modify_parameter(bts, 'jobType', value)

    def get_cell_srperiod(self, bts, case):
        value = '5ms' if case.case_type.strip().upper() in ['PING_DELAY_32','PING_DELAY_1500','PING_DELAY_1400'] else '40ms'
        value = '10ms' if case.on_demand_uplink_scheduling.strip() == 'Y' else value
        if not bts.airscale:
            return modify_parameter(bts, 'cellSrPeriod', value)
        else:
            return []

