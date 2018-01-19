from petbase import *

class c_tm500_script_builder(object):
    def __init__(self, bts = None, sbts = None):
        self.bts = bts
        self.sbts = sbts
        self.case = gv.case.curr_case
        self.script = []
        self.uegroups = []
        self.startusim = ''
        self.startue = 0
        self.start_delay = 0

        self.ue_group_count = 0
        self.traffic_profile_count = 0
        self.traffic_modal_count = 0
        self.mobile_modal_count = 0
        self.path_count = 0

        self.traffic_modal_list = []
        self.mobile_modal_list = []

        self.bandlist = self.case.band.upper().replace('M', '').split('-')
        self.bandlist = self.bandlist * int(len(bts.lncels)/len(self.bandlist))

        self.cell_count = len(self.bts.lncels)
        self.phycelllist = self.bts.phycellid_list

        self.tm1, self.tm2 = 2, 2
        self.tm1 = 4 if self.case.tm in ['4X2', '4X2-TM4X2', 'TM4X2-TM4X2', '4X2-4X2'] else self.tm1
        if self.case.tm in ['1']:
            self.tm1, self.tm2 = 1, 1
        self.uldl = self.case.uldl
        self.ssf = self.case.ssf
        self.antennas = '4' if self.case.tm.strip().upper() in ['4X2','4X2-TM4X2','4X2-TM4X2-TM4X2', 'TM4X2-TM4X2', '4X2-4X2'] else '2'
        self.antennas = '1' if self.case.tm.strip().upper() in ['1', '1-TM1', 'TM1-TM1', '1-TM1-TM1'] else self.antennas


    def _get_usim_str(self, startusim):
        tsr = 'forw mte UsimConfig 1([%s+1 2] [] [] [] []) [] [] '%(startusim)
        tsr += '[00112233445566778899AABBCCDDEEFF] [01020304050607080910111213141516 '
        tsr += '00000000000000000000000000000000 00000000000000000000000000000001 '
        tsr += '00000000000000000000000000000002 00000000000000000000000000000004 '
        tsr += '00000000000000000000000000000008 64 0 32 64 96 []] [] []'
        return tsr

    def _get_usim_str_2(self,startusim):
        tsr = 'forw mte UsimConfig 1([%s+1 2] [] [] [] []) [] [] '%(startusim)
        tsr += '[A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5] [CDC202D5123E20F62B6D676AC72CB318  '
        tsr += '00000000000000000000000000000000 00000000000000000000000000000001 '
        tsr += '00000000000000000000000000000002 00000000000000000000000000000004 '
        tsr += '00000000000000000000000000000008 64 0 32 64 96 []] [] []'
        return tsr

    def set_service(self, number = 0,
                          application = 'DL_UDP_lp0',
                          load_profile = -1,
                          bear_alloc = 0,
                          service_delay = 0,
                          service_duration = 0,
                          service_repeat = 1):
        return '%s(%s %s) %s [%s %s %s]' %( number,
                                            application,
                                            load_profile,
                                            bear_alloc,
                                            service_delay,
                                            service_duration,
                                            service_repeat)

    def set_service2(self, number = 0,
                          application = 'DL_UDP_lp0',
                          load_profile = -1,
                          bear_alloc = 0,
                          service_delay = 0,
                          service_duration = 0,
                          service_repeat = 1):
        return '%s(%s %s) %s []' %( number,
                                            application,
                                            load_profile,
                                            bear_alloc)

    def set_apn(self, apn_name = '', servicelist=[]):
        return '%s '+ ','.join(servicelist)

    def set_enb_position_entity(self,
                                id = 0,
                                x = 0,
                                y = 0,
                                cell_count = 1,
                                cell_id = 0,
                                dl_frequency = 0,
                                cell_range = 0,
                                sector_start = 0,
                                sector_end = 0,
                                ante_gain = 0,
                                ante_model = 0,
                                sector_off = 0,
                                ref_signal_power = 0):
        cell_range = self.case.cell_range
        sector_start = self.case.sector_start
        sector_end = self.case.sector_end
        ref_signal_power = self.case.ref_signal_power
        return '%s %s %s %s{%s %s %s [%s %s %s %s(%s)] [%s]}' %(
                    id, x, y, cell_count, cell_id, dl_frequency, cell_range,
                    sector_start, sector_end, ante_gain, ante_model,
                    sector_off, ref_signal_power)

    def config_env_value(self, key, value):
        self.script.append('SETP %s %s' %(key, value))

    def config_raw(self, instr):
        self.script.append(instr)

    def config_antennas(self):
        self.script.append('SETP RRC_NUM_DL_ANTENNAS ' + self.antennas)

    #----------------------------------------------
    # Set the cell information for a radio context
    #----------------------------------------------
    # PARAMETERS
    # 1. Radio Context Id
    # 2. Cell Id
    # 3. DL carrier frequency
    # 4. System Bandwidth
    # 5. Number of eNB transmit antennas
    # 6. Subframe Assignment
    # 7. Special Subframe Patttern
    # 8. Number of receive antennas
    #----------------------------------------------
    #                                 1 2 3     4   5   6 7   8
    #                                 | | |     |   |   | |   |
    # forw mte SetMueRadioContextCell 0 4 23400 20 [2] [1 7] [2]
    def config_rf_card(self, rcindex, bts, physical_cell_id, frequency, band):
        self.script.append('forw mte  SetMueRadioContextCell %s %s %s %s [%s] [%s %s] [%s]' %(
                            rcindex,
                            physical_cell_id,
                            frequency,
                            band,
                            self.tm1,
                            self.uldl,
                            self.ssf,
                            self.tm2))

    ##################################
    # TEST STEP: Start RDA Test Case #
    ##################################

    #-------------------------------------------------------
    # Configure and start a Real Data Application Test Case
    #-------------------------------------------------------
    # PARAMETERS
    # 1. Test system type
    # 2. Test system control IP address
    # 3. TM500 user ID
    # 4. Test case name
    #-------------------------------------------------------
    #                                   1 2               3   4
    #                                   | |               |   |
    # forw mte DeConfigRdaStartTestCase 0 192.168.10.200 [4] [Mixed_UDP_FTP_600UEs]
    #-------------------------------------------------------
    def config_shenick(self):
        self.script.append('forw mte DeConfigRdaStartTestCase 0 %s [%s] [%s]' %(
                            gv.tm500.shenick_hostname,
                            gv.tm500.shenick_partition,
                            gv.tm500.shenick_volte_group_name))
        self.script.append('WAIT FOR "I: CMPI DTE RDA TEST GROUP STARTED IND:"')

        #-------------------------------------------------------
    # Configure and start a Real Data Application Test Case
    #-------------------------------------------------------
    # PARAMETERS
    # 1. Test system type
    # 2. Test system control IP address
    # 3. TM500 user ID
    # 4. Test case name
    #-------------------------------------------------------
    #                                   1 2               3   4
    #                                   | |               |   |
    # forw mte DeConfigRdaStartTestCase 0 192.168.10.200 [4] [Mixed_UDP_FTP_600UEs]
    #-------------------------------------------------------
    def config_shenick_group(self,group_name):
        self.script.append('forw mte DeConfigRdaStartTestCase 0 %s [%s] [%s]' %(
                            gv.tm500.shenick_hostname,
                            gv.tm500.shenick_partition,
                            group_name))
        self.script.append('WAIT FOR "I: CMPI DTE RDA TEST GROUP STARTED IND:"')
    ############################################
    # TEST STEP: Configure Uplink Power Offset #
    ############################################

    #-----------------------------------------------
    # Set the uplink power offsets for multiple UEs
    #-----------------------------------------------
    # PARAMETERS
    # 1. Number of UEs
    # 2. UE Context Id
    # 3. PUCCH Power Offset
    # 4. PRACH Power Offset
    # 5. PUSCH Power Offset
    # 6. SRS Power Offset
    #-----------------------------------------------
    #                                 1 2  3  4   5
    #                                 | |  |  |   |
    # forw mte PhyConfigUlPowerOffset 1{-1 66 66 [66] []}
    #-----------------------------------------------
    def config_ul_offset(self, pucch_offset, pracch_offset, pusch_offset):
        # self.script.append('forw mte PhyConfigUlPowerOffset 1{-1 %s %s [%s] []}' %(
        #                     pucch_offset,
        #                     pracch_offset,
        #                     pusch_offset))
        self.script.append('forw mte PhyCalibrateUlPowerOffset')


    #-----------------------------------------------
    # Set the uplink power offsets for multiple UEs
    #-----------------------------------------------
    # PARAMETERS
    # 1. Number of UEs
    # 2. UE Context Id
    # 3. PUCCH Power Offset
    # 4. PRACH Power Offset
    # 5. PUSCH Power Offset
    # 6. SRS Power Offset
    #-----------------------------------------------
    #                                 1 2  3  4   5
    #                                 | |  |  |   |
    # forw mte PhyConfigUlPowerOffset 1{-1 66 66 [66] []}
    #-----------------------------------------------
    def config_ul_power_offset(self, pucch_offset, pracch_offset, pusch_offset):
        self.script.append('forw mte PhyConfigUlPowerOffset 1{-1 %s %s [%s] []}' %(
                            pucch_offset,
                            pracch_offset,
                            pusch_offset))
        #self.script.append('forw mte PhyCalibrateUlPowerOffset')
    #-----------------------
    # Defines a set of UEs.
    #-----------------------
    # PARAMETERS
    # 1. UE Group Id
    # 2. UE Group Type
    # 3. Number of entries
    # 4. UE Context Id
    #-----------------------
    #                           1 2 3 4
    #                           | | | |
    # forw mte MtsConfigUeGroup 0 0 1{0-9}
    #-----------------------
    #----------------------------------------------------------------------------
    # Defines a collective UE group context to apply to specific per UE commands
    #----------------------------------------------------------------------------
    # PARAMETERS
    # 1. UE Group Id
    #----------------------------------------------------------------------------
    #                            1
    #                            |
    # forw mte SetUEGroupContext 0
    #----------------------------------------------------------------------------

    #---------------------
    # Configures the USIM
    #---------------------
    # PARAMETERS
    # 1.  USIM Type
    # 2.  IMSI
    # 3.  MNC Length
    # 4.  Authentication Key
    # 5.  OP
    # 6.  C1
    # 7.  C2
    # 8.  C3
    # 9.  C4
    # 10. C5
    # 11. R1
    # 12. R2
    # 13. R3
    # 14. R4
    # 15. R5
    #---------------------
    #                                                                                                                                                                                                                                                                       1                                1  1 1  1  1
    #                     1  2                 3                      4                                  5                                6                                7                                8                                9                                0                                1  2 3  4  5
    #                     |  |                 |                      |                                  |                                |                                |                                |                                |                                |                                |  | |  |  |
    # forw mte UsimConfig 1([262030020030001+1 2] [] [] [] []) [] [] [00112233445566778899AABBCCDDEEFF] [01020304050607080910111213141516 00000000000000000000000000000000 00000000000000000000000000000001 00000000000000000000000000000002 00000000000000000000000000000004 00000000000000000000000000000008 64 0 32 64 96 []] [] []
    #---------------------
    def config_ue_group(self, grouptype, startueid, ue_count, startimsi, aptstring):
        self.script.append('forw mte MtsConfigUeGroup %s %s 1{%s-%s}' %(
                            self.ue_group_count,
                            grouptype,
                            startueid,
                            startueid + int(ue_count) -1))
        self.script.append('forw mte SetUEGroupContext %s' %(self.ue_group_count))
        self.script.append(self._get_usim_str(startimsi))
        if aptstring:
            self.script.append('forw mte RrcAptConfigUeCap ' + aptstring)
        self.ue_group_count += 1
        return self.ue_group_count-1

    def config_ue_group2(self, grouptype, startueid, ue_count, startimsi, aptstring):
        self.script.append('forw mte MtsConfigUeGroup %s %s 1{%s-%s}' %(
                            self.ue_group_count,
                            grouptype,
                            startueid,
                            startueid + int(ue_count) -1))
        self.script.append('forw mte SetUEGroupContext %s' %(self.ue_group_count))
        if self.case.domain in ['CAP']:
            if self.case.ue_is_m678:
                self.script.append('forw mte UsimConfig 1([%s+1 2] [] [] [] []) [] [] [A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5A5] [] [] []' %(startimsi))
            elif self.case.ue_is_mdrb and (gv.tm500.tm500_id == '34' or gv.tm500.tm500_id == '35'):
                self.script.append(self._get_usim_str_2(startimsi))
            else:
                self.script.append(self._get_usim_str(startimsi))
        else:
            self.script.append(self._get_usim_str(startimsi))
        if aptstring:
            self.script.append('forw mte RrcAptConfigUeCap ' + aptstring)
        self.ue_group_count += 1
        return self.ue_group_count-1

    def config_ue_group3(self, grouptype, startueid, ue_count):
        self.script.append('forw mte MtsConfigUeGroup %s %s 1{%s-%s}' %(
                            self.ue_group_count,
                            grouptype,
                            startueid,
                            startueid + int(ue_count) -1))
        self.ue_group_count += 1
        return self.ue_group_count-1


    def define_ue_group(self, grouptype, startueid, ue_count):
        self.script.append('forw mte MtsConfigUeGroup %s %s 1{%s-%s}' %(
                            self.ue_group_count,
                            grouptype,
                            startueid,
                            startueid+ue_count))
        self.ue_group_count+=1
        return self.ue_group_count-1

    def define_ue_group2(self, ue_group_id, grouptype, startueid, ue_count):
        self.script.append('forw mte MtsConfigUeGroup %s %s 1{%s-%s}' %(
                            ue_group_id,
                            grouptype,
                            startueid,
                            startueid+ue_count))
        return ue_group_id

    #-------------------------------------------
    # Configure the physical layer capabilities
    #-------------------------------------------
    # PARAMETERS
    # 1. Number of UE downlink antennae
    # 2. DL UE category
    # 3. UL UE category
    #-------------------------------------------
    #                          1 2 3
    #                          | | |
    # forw mte PhyConfigSysCap 2 4 4
    #-------------------------------------------
    def config_phy_cap(self):
        if hasattr(self.case, 'ue_cap'):
            if self.case.ue_cap.strip():
                value = '2 6 6' if self.case.ue_cap.strip() <> 'NCA' else '2 4 4'
            else:
                value = '2 6 6' if self.case.ca_type.strip() else '2 4 4'
            value = '2 4 5' if self.case.cat5 else value
            self.script.append('forw mte PhyConfigSysCap %s' %(value))

    #----------------------------------------------
    # Configures the NAS to select a specific PLMN
    #----------------------------------------------
    # PARAMETERS
    # 1. Force PLMN
    #----------------------------------------------
    #                                    1
    #                                    |
    # forw mte NasAptConfigPlmnSelection 26203
    #----------------------------------------------
    def config_nas_plmn(self, plmn = '26203'):
        self.script.append('forw mte NasAptConfigPlmnSelection ' + plmn)

    #-----------------------------------------------------------------------------
    # Defines the physical position of a set of LTE eNBs and the associated cells
    #-----------------------------------------------------------------------------
    # PARAMETERS
    # 1.  Number of entries
    # 2.  eNB Id
    # 3.  eNB X
    # 4.  eNB Y
    # 5.  Number of cells
    # 6.  Cell Id
    # 7.  DL frequency
    # 8.  Cell range
    # 9.  Sector start
    # 10. Sector end
    # 11. Antenna gain
    # 12. Antenna model
    # 13. Sector rolloff
    # 14. Reference Signal Power
    # 17. Enhanced measurement
    #-----------------------------------------------------------------------------
    #                                                    1   1 1 1    1                             1   1 1 1    1
    #                       1 2 3    4 5 6 7     8     9 0   1 2 3    4   2 3   4 5 6 7     8     9 0   1 2 3    4
    #                       | | |    | | | |     |     | |   | | |    |   | |   | | | |     |     | |   | | |    |
    # forw mte MtsConfigEnb 2{0 -500 0 1{4 23400 1000 [0 360 0 0(0)] [6]},1 500 0 1{3 23400 1000 [0 360 0 0(0)] [6]}}
    #-----------------------------------------------------------------------------

    def config_enb_position(self, entity_list = []):
        tstr = 'forw mte MtsConfigEnb %d{%s}' %(len(entity_list),
                ','.join(entity_list))
        self.script.append(tstr)

    #--------------------------------------------
    # Defines the path to be used by a UE group.
    #--------------------------------------------
    # PARAMETERS
    # 1. Path ID
    # 2. Number of waypoints
    # 3. WP X
    # 4. WP Y
    #--------------------------------------------
    #                        1 2 3    4
    #                        | | |    |
    # forw mte MtsConfigPath 0 1{1100 0}
    #--------------------------------------------
    def config_path(self, points): #usage: config_path(0, {'1':(300,300), '2':(400,400)})
        tstr = 'forw mte MtsConfigPath %d %d{' %(self.path_count, len(points))
        for point in points.values():
            tstr += '%s %s,' %(point[0], point[1])
        tstr = tstr[:-1] + '}'
        self.script.append(tstr)
        self.path_count += 1
        return self.path_count - 1

    #----------------------------------------------------
    # Defines the mobility behaviour for a group of UEs.
    #----------------------------------------------------
    # PARAMETERS
    # 1. MM ID
    # 2. UE group ID
    # 3. Path ID
    # 4. Path end
    # 5. Position distribution
    # 6. Average speed
    # 7. Speed distribution
    # 8. Ioc
    #----------------------------------------------------
    #                            1 2 3 4 5 6 7 8
    #                            | | | | | | | |
    # forw mte MtsConfigMobility 0 6 0 0 0 0 0 -140
    #----------------------------------------------------
    def config_mobility(self,
                              groupid = 0,
                              pathid  = 0,
                              pathend = 0,
                              position_distribution = 0,
                              speed = 0,
                              speed_distribution = 0,
                              ioc = 140,
                              fading = 0):
        self.script.append('forw mte MtsConfigMobility %s %s %s %s %s %s %s -%s [%s]' %(
                                    self.mobile_modal_count,
                                    groupid,
                                    pathid,
                                    pathend,
                                    position_distribution,
                                    speed,
                                    speed_distribution,
                                    ioc,
                                    fading))
        self.mobile_modal_list.append(self.mobile_modal_count)
        self.mobile_modal_count += 1
        return self.mobile_modal_count -1

    #----------------------------------------------------------
    # Defines the traffic profiles to be applied to UE groups.
    #----------------------------------------------------------
    # PARAMETERS
    # 1.  Traffic Profile ID
    # 2.  Number of PDN
    # 3.  APN
    # 4.  Number of services
    # 4a. Service name type
    # 4b. Application/Command
    # 4c. Load profile
    # 4d. Bearer allocation
    # 4e. Filter definition
    # 4f. Service delay timer
    # 4g. Service duration
    # 4h. Service repeat
    # 5.  PDN Type
    #----------------------------------------------------------
    #                                           4 4          4   4  4 4 4
    #                                  1 2 3  4 a b          c   d  f g h
    #                                  | | |  | | |          |   |  | | |
    # forw mte MtsConfigTrafficProfile 0 1{"" 1{0(DL_UDP_lp0 -1) 0 [0 0 1]} [] []} []
    # forw mte MtsConfigTrafficProfile 1 2{internet.nsn.com 1{0("" -1) 0 [60 0 1]} [] [] [],srvcc.nsn.com 0{} [] [] []} []

    # forw mte MtsConfigTrafficProfile 0 2{internet.nsn.com 0{} [] [],srvcc.nsn.com 1{0(cvoip -1) 1 [0 0 1]} [] []} []',
    # forw mte MtsConfigTrafficProfile 0 2{internet.nsn.com 2{0(cftp_get -1 ) 0 [0 0 1],0(cftp_put -1 ) 0 [0 0 1]} [] [] [],srvcc.nsn.com 1{0(cvoip -1 ) 1 [0 0 1]} [] [] [] } []
    #----------------------------------------------------------
    def config_traffic_profile(self,
                                     pdn_number = 1,
                                     apn = '',
                                     servicelist = []):
        tstr = 'forw mte MtsConfigTrafficProfile %s %s{"%s" %d{%s} [] []} []' %(
                       self.traffic_profile_count,
                       pdn_number,
                       apn,
                       len(servicelist),
                       ','.join(servicelist))
        self.script.append(tstr)
        self.traffic_profile_count += 1
        return self.traffic_profile_count-1

    #----------------------------------------------------------------------------------------
    # Defines the UE registration behaviour for a UE group and associates a traffic profile.
    #----------------------------------------------------------------------------------------
    # PARAMETERS
    # 1. TM ID
    # 2. UE group ID
    # 3. Traffic profile ID
    # 4. Attach start delay
    # 5. Attach duration
    # 6. Detach duration
    # 7. Time distribution
    # 8. Stagger time
    #----------------------------------------------------------------------------------------
    #                           1 2 3  4 5 6 7  8
    #                           | | |  | | | |  |
    # forw mte MtsConfigTraffic 0 0 0 [0 0 0 -1(50)]
    # forw mte MtsConfigTraffic 0 0 2 [0 0 0 0(40)]
    #----------------------------------------------------------------------------------------
    def config_uegroup_traffic_profile(self,
                                             groupid = 0,
                                             traffic_profile_id = 0,
                                             attach_start_delay = 0,
                                             attach_duration = 0,
                                             deattach_duration = 0,
                                             time_distribution = 0,
                                             stagger_timer = 50):
        self.script.append('forw mte MtsConfigTraffic %s %s %s [%s %s %s %s(%s)]' %(
                                             self.traffic_modal_count,
                                             groupid,
                                             traffic_profile_id,
                                             attach_start_delay,
                                             attach_duration,
                                             deattach_duration,
                                             time_distribution,
                                             stagger_timer))
        self.traffic_modal_list.append(self.traffic_modal_count)
        self.traffic_modal_count += 1
        return self.traffic_modal_count -1
    #----------------------------------------------------------------------------------------
    # Defines the UE registration behaviour for a UE group and associates a traffic profile.
    #----------------------------------------------------------------------------------------
    # PARAMETERS
    # 1. TM ID
    # 2. UE group ID
    # 3. Traffic profile ID
    # 4. Attach start delay
    # 5. Attach duration
    # 6. Detach duration
    # 7. Time distribution
    # 8. Stagger time
    #----------------------------------------------------------------------------------------
    #                           1 2 3  4 5 6 7  8
    #                           | | |  | | | |  |
    # forw mte MtsConfigTraffic 0 0 0 [0 0 0 -1(50)]
    # forw mte MtsConfigTraffic 0 0 2 [0 0 0 0(40)]
    #----------------------------------------------------------------------------------------
    def config_uegroup_traffic_profile2(self,
                                             groupid = 0,
                                             traffic_profile_id = 0,
                                             attach_start_delay = 0,
                                             attach_duration = 0,
                                             deattach_duration = 0,
                                             time_distribution = 0,
                                             stagger_timer = 50):
        self.script.append('forw mte MtsConfigTraffic %s %s %s [%s %s %s %s(%s)]' %(
                                             self.traffic_modal_count,
                                             groupid,
                                             traffic_profile_id,
                                             attach_start_delay,
                                             attach_duration,
                                             deattach_duration,
                                             time_distribution,
                                             stagger_timer))
        self.traffic_modal_list.append(self.traffic_modal_count)
        self.traffic_modal_count += 1
        #self.traffic_profile_id += 1
        return self.traffic_modal_count -1
    # Configures the complete MTS scenario as a series of sequences each with a designated duration.
    #------------------------------------------------------------------------------------------------
    # PARAMETERS
    # 1.  Number of MTS sequences
    # 2.  Duration
    # 3.  Number of MM
    # 3a. MM ID
    # 3b. MM action
    # 4.  Number of TM
    # 4a. TM ID
    # 4b. TM action
    # 6.  Action mismatch handling
    # 7.  UE mismatch handling
    #------------------------------------------------------------------------------------------------
    #                                       3 3 3 3 3 3    4 4 4 4 4 4 4 4 4 4 4 4
    #                            1 2      3 a b a b a b  4 a b a b a b a b a b a b          6   7
    #                            | |      | | | | | | |  | | | | | | | | | | | | |          |   |
    # forw mte MtsConfigScenario 1{259200 3{0 0,1 0,2 0} 6{0 0,1 0,2 0,3 0,4 0,5 0} []} [] [0] [0]
    #------------------------------------------------------------------------------------------------
    def config_mts_scenario(self, duration):
        tstr = 'forw mte MtsConfigScenario 1{%s %s{%s} %s{%s} []} [] [0] [0]' %(
            duration,
            len(self.mobile_modal_list),
            ','.join(['%s 0' %(mmid) for mmid in self.mobile_modal_list]),
            len(self.traffic_modal_list),
            ','.join(['%s 0' %(tmid) for tmid in self.traffic_modal_list]))
        self.script.append(tstr)
    #------------------------------------------------------------------------------------------------
    # PARAMETERS
    # 1.  Number of MTS sequences
    # 2.  Duration
    # 3.  Number of MM
    # 3a. MM ID
    # 3b. MM action
    # 4.  Number of TM
    # 4a. TM ID
    # 4b. TM action
    # 6.  Action mismatch handling
    # 7.  UE mismatch handling
    # 8.  Status level
    #------------------------------------------------------------------------------------------------
    #                                  4 4
    #                          1 2 3 4 a b          6   7      8
    #                          | | | | | |          |   |      |
    #forw mte MtsConfigScenario 1{0 0 1{0 0} []} [] [0] [0] [] [0]
    def config_mts_scenario2(self):
        tstr = 'forw mte MtsConfigScenario 1{0 0 1{0 0} []} [] [0] [0] [] [0]'
        self.script.append(tstr)
    #--------------------------------
    # Activate pending configuration
    #--------------------------------
    # PARAMETERS
    # 1. Timing Type
    #--------------------------------
    #                   1
    #                   |
    # forw mte Activate -1
    #--------------------------------
    def config_execute_script(self):
        self.script.append('forw mte Activate -1')

    def config_nas_cap(self, Ciphering=224, Integrity=224, nas_release=3):
        self.script.append('forw mte NasAptConfigCapability [] [%s] [%s] [] [] [%s]' %(Ciphering,
            Integrity, nas_release))

    def config_cell_section(self, cellid=''):
        self.script.append('forw mte RrcAptConfigCellSelection %s %s' %(self.bts.dl_frequency_pcell, cellid))

    def config_cell_section2(self, dl_frequency='', cellid=''):
        self.script.append('forw mte RrcAptConfigCellSelection %s %s' %(dl_frequency, cellid))

    def clear_scenarios(self):
        self.script.append('forw mte mtsclearmts')

    def env_config_for_mts(self):
        self.config_env_value('NAS_ENABLE_INDICATIONS_IN_MTS_MODE', 1)
        # self.config_env_value('ENABLE_AUTO_SYS_INFO_ACQ_AT_STARTUP', 1)
        self.config_env_value('RRC_PUCCH_CLOSE_LOOP_POWER_CONTROL', 0)
        self.config_env_value('L2_MAC_ENABLE_CR379_R2_094167', 1)
        self.config_env_value('L2_MAC_ENABLE_REL_9_CR409', 1)
        self.config_env_value('RRC_ENABLE_RELEASE_10', 1)
        self.config_env_value('NAS_ENABLE_R10', 1)
        self.config_raw('FORW L1 Msg4BypassContentionResolution 1')

    def config_ue_cap(self, capstr):
        self.script.append('forw mte RrcAptConfigUeCap [[] [] [] [] [] [] [1{0 %s}]]' %(capstr))

    def build_a_service(self, name_type = '0',
                              application = '',
                              load_profile = '-1',
                              bear_alloc = '0',
                              filter_defination = '',
                              service_delay = '0',
                              service_duration = '0',
                              service_repeat = '1'):
        return '%s(%s %s) %s [%s %s %s]' %(name_type,
                                           application,
                                           load_profile,
                                           bear_alloc,
                                           service_delay,
                                           service_duration,
                                           service_repeat)
    def build_service_list(self, servicelist=[]):
        return str(len(servicelist)) + '{%s}' %(','.join(servicelist))

    def build_a_apn(self, apn_name = '', serivce_list_for_apn = []):
        return  '%s %s [] [] []' %(apn_name, self.build_service_list(serivce_list_for_apn))

    def build_apn_list(self, apn_list = []):
        return '{%s}' %(','.join(apn_list))

    def config_traffic_profile2(self,
                                 pdn_number = 1,
                                 apn_list = []):
        tstr = 'forw mte MtsConfigTrafficProfile %s %s%s []' %(
                       self.traffic_profile_count,
                       pdn_number,
                       self.build_apn_list(apn_list))
        self.script.append(tstr)
        self.traffic_profile_count += 1
        return self.traffic_profile_count-1

    def set_enb_position_entity2(cell_id = 0,
                             dl_frequency = 0,
                             cell_range = 0,
                             ref_signal_power = 0):
        return '%s %s %s [] [%s]' %(cell_id, dl_frequency, cell_range, ref_signal_power)
