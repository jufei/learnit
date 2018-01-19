import os
import copy
from pet_ipalib import IpaMmlItem, IpaMmlDict


tm500_log_type_for_latency = [
                                'DLL1L2CONTROL',
                                'L1DLRSPOWER',
                                'MACRX',
                                'MACTX',
                                'PRACHTX',
                                'ProtocolLog',
                                ]
tm500_log_type_for_through = [
                                # 'CQIREPORTING',
                                # 'DLL1L2CONTROL',
                                # 'DLSCHRX',
                                'L1DLRSPOWER',
                                # 'L1THROUGHPUT',
                                'ProtocolLog',
                                'UEOVERVIEW',
                                # 'ULHARQTX',
                                # 'ULSCHTX',
                                # 'ULSRS',
                                'SCCSTATUS',
                                ]
tm500_log_type_for_ping = ['ProtocolLog',]

tm500_log_type_for_ho = [
                                'MACRX',
                                'MACTX',
                                ]

tm500_log_type_for_volte = [
                                'MACRX',
                                # 'MACTX',
                                ]


tm500_version_for_throughput = 'TM500_APPLICATION_K_VERSION_DIR'
tm500_version_for_volte = 'TM500_APPLICATION_L_VERSION_DIR'

all_cases = IpaMmlDict()

#Case_throughput
#Case_FTP_TEST  this case is kept for RL55
case = IpaMmlItem()
case.case_name          =        'THROUGHPUT'
case.tm500_version      = tm500_version_for_throughput
case.tm500_log_types    = tm500_log_type_for_through
case.ta_steps = {
            'setup'        :    'common_test_case_setup_for_throughput',
            'document'     :    'Document about this case',
            'tags'         :     ['FTP_TEST'],
            'Timeout'      :     '30 minute',
            'steps'        :[
                            ['Pet ue attach'],
                            ['set_tm500_log_types'],
                            ['setup_pppoe_on_data_device'],
                            ['setup_pppoe_on_data_device'],

                            ['start_ftp_download_on_data_device'],
                            ['wait_until_ftp_download_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpdl'],
                            ['stop_ftp_download_on_data_device'],
                            ['run_keyword_and_record_error', 'verify_counter_files'],

                            ['start_ftp_upload_on_data_device'],
                            ['wait_until_ftp_upload_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpul'],
                            ['stop_ftp_upload_on_data_device'],
                            ['run_keyword_and_record_error', 'verify_counter_files'],

                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_throughput',
                        }
all_cases[case.case_name] = case

#Case_FTP_TEST_CA #without no  upload, only for RL55
case = IpaMmlItem()
case.case_name = 'THROUGHPUT_CA'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_through
case.ta_steps = {
            'setup'        :    'common_test_case_setup_for_throughput',
            'document'    :    'Document about this case',
            'tags'        :     ['FTP_TEST_CA'],
            'steps'        :[
                            ['Pet ue attach'],
                            ['set_tm500_log_types'],
                            ['setup_pppoe_on_data_device'],

                            ['start_ftp_download_on_data_device'],
                            ['wait_until_ftp_download_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpdl'],
                            ['stop_ftp_download_on_data_device'],

                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_throughput',
                        }
all_cases[case.case_name] = case

#Throughput for FTP
case = IpaMmlItem()
case.case_name = 'FTP_DOWNLOAD'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_through
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_throughput',
            'document'    :    'Document about this case',
            'tags'        :     ['FTP_DOWNLOAD', 'THROUGHPUT'],
            'steps'        :[
                            ['Pet ue attach'],
                            ['set_tm500_log_types'],
                            ['setup_pppoe_on_data_device'],

                            ['start_ftp_download_on_data_device'],
                            ['wait_until_ftp_download_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpdl'],
                            ['stop_ftp_download_on_data_device'],

                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_throughput',
                        }
all_cases[case.case_name] = case

case = IpaMmlItem()
case.case_name = 'FTP_UPLOAD'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_through
case.ta_steps = {
            'setup'        :    'common_test_case_setup_for_throughput',
            'document'    :    'Document about this case',
            'tags'        :     ['FTP_UPLOAD', 'THROUGHPUT'],
            'steps'        :[
                            ['Pet ue attach'],
                            ['set_tm500_log_types'],
                            ['setup_pppoe_on_data_device'],

                            ['start_ftp_upload_on_data_device'],
                            ['wait_until_ftp_upload_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpul'],
                            ['stop_ftp_upload_on_data_device'],

                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_throughput',
                        }
all_cases[case.case_name] = case

#Case Latency
case = IpaMmlItem()
case.case_name = 'LATENCY'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_latency
case.ta_steps = {
                'setup'        :    'common_test_case_setup_for_latency',
                'document'    :    'Document about this case',
                'tags'        :     ['LATENCY'],
                'steps'        :[
                                ['start_tshark_on_bts'],
                                ['set_tm500_log_types'],
                                ['pet_start_tm500_logging'],
                                ['Pet ue attach'],
                                ['sleep', '2s'],
                                ['stop_tm500_logging_and_download_logs'],
                                ['stop_tshark_and_parse_file'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_tput_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_latency',
                        }
all_cases[case.case_name] = case


#Case Network Trigger
case = IpaMmlItem()
case.case_name = 'NETWORK_TRIGGER'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_latency
case.ta_steps = {
                'setup'        :    'common_test_case_setup_for_latency',
                'document'    :    'Document about this case',
                'tags'        :     ['TRIGGER'],
                'steps'        :[
                                ['start_tshark_on_bts'],
                                ['set_tm500_log_types'],
                                ['pet_start_tm500_logging'],
                                ['Pet ue attach'],
                                ['wait_until_ue_deattached'],
                                ['try_to_trigger_ue_by_ping_operation'],
                                ['wait_until_ue_re_attached'],
                                ['stop_tm500_logging_and_download_logs'],
                                ['stop_tshark_and_parse_file'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_tput_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_latency',
                        }
all_cases[case.case_name] = case

#Case UE Trigger
case = IpaMmlItem()
case.case_name = 'UE_TRIGGER'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_latency
case.ta_steps = {
                'setup'        :    'common_test_case_setup_for_latency',
                'document'    :    'Document about this case',
                'tags'        :     ['TRIGGER'],
                'steps'        :[
                                ['start_tshark_on_bts'],
                                ['set_tm500_log_types'],
                                ['pet_start_tm500_logging'],
                                ['Pet ue attach'],
                                ['wait_until_ue_deattached'],
                                ['setup_pppoe_on_data_device'],
                                ['ping_from_data_device', '1', '2', '32'],
                                ['wait_until_ue_re_attached'],
                                ['stop_tm500_logging_and_download_logs'],
                                ['stop_tshark_and_parse_file'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_tput_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_latency',
                        }
all_cases[case.case_name] = case


#Case Ping Delay 32
case = IpaMmlItem()
case.case_name = 'PING_DELAY_32'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_ping
case.ta_steps = {
                'setup'       :    'common_test_case_setup_for_ping_delay',
                'document'    :    'Document about this case',
                'tags'        :     ['PING_DELAY'],
                'steps'        :[
                                ['Pet ue attach'],
                                # ['setup_pppoe_connection'],
                                # ['ping_from_ue_to_bts', '50', '8', '32'],
                                ['setup_pppoe_on_data_device'],
                                ['ping_from_data_device', '50', '8', '32'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_tput_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_ping_delay',
                        }
all_cases[case.case_name] = case

#Case Ping Delay 1400
case = IpaMmlItem()
case.case_name = 'PING_DELAY_1400'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_ping
case.ta_steps = {
                'setup'        :   'common_test_case_setup_for_ping_delay',
                'document'    :    'Document about this case',
                'tags'        :     ['PING_DELAY'],
                'steps'        :[
                                ['Pet ue attach'],
                                # ['setup_pppoe_connection'],
                                # ['ping_from_ue_to_bts', '50', '8', '1400'],
                                ['setup_pppoe_on_data_device'],
                                ['ping_from_data_device', '50', '8', '1400'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_tput_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_ping_delay',
                        }
all_cases[case.case_name] = case

#Case Ping Delay 1500
case = IpaMmlItem()
case.case_name = 'PING_DELAY_1500'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = tm500_log_type_for_ping
case.ta_steps = {
                'setup'        :    'common_test_case_setup_for_ping_delay',
                'document'    :    'Document about this case',
                'tags'        :     ['PING_DELAY'],
                'steps'        :[
                                ['Pet ue attach'],
                                # ['setup_pppoe_connection'],
                                # ['ping_from_ue_to_bts', '50', '8', '1400'],
                                ['setup_pppoe_on_data_device'],
                                ['ping_from_data_device', '50', '8', '1500'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_tput_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_ping_delay',
                        }
all_cases[case.case_name] = case

#Case Volte_capacity
case = IpaMmlItem()
case.case_name = 'VOLTE_CAP'
case.tm500_version = tm500_version_for_volte
case.tm500_log_types = tm500_log_type_for_volte
case.ta_steps = {
                'setup'        :    'common_test_case_setup_for_volte',
                'document'    :    'Document about this case',
                'tags'        :     ['VOLTE_CAP'],
                'steps'        :[
                                ['pet_ue_attach_for_volte'],
                                ['wait_until_volte_service_is_done'],
                                ['retrieve_shenick_statistic_result'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_volte_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_volte',
                        }
all_cases[case.case_name] = case


#Case Volte_call_setup
case = IpaMmlItem()
case.case_name = 'VOLTE_CALL_SETUP'
case.tm500_version = tm500_version_for_volte
case.tm500_log_types = tm500_log_type_for_volte
case.ta_steps = {
                'setup'       :    'common_test_case_setup_for_volte',
                'document'    :    'Document about this case',
                'tags'        :     ['VOLTE_CALL_SETUP'],
                'steps'        :[
                                ['repeat_to_do_ue_call_drop_for_specific_time', '10'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_volte_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_volte',
                        }
all_cases[case.case_name] = case

#Case Volte_call_drop
case = IpaMmlItem()
case.case_name = 'VOLTE_CALL_DROP'
case.tm500_version = tm500_version_for_volte
case.tm500_log_types = tm500_log_type_for_volte
case.ta_steps = {
                'setup'       :    'light_test_case_setup_for_pet',
                'document'    :    'Document about this case',
                'tags'        :     ['VOLTE_CALL_DROP'],
                'steps'        :[
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_volte_should_be_ok'],
                            ],
                'teardown'    :'light_test_case_teardown_for_pet',
                        }
all_cases[case.case_name] = case

#Case Volte_call_setup
case = IpaMmlItem()
case.case_name = 'VOLTE_PERM'
case.tm500_version = tm500_version_for_volte
case.tm500_log_types = tm500_log_type_for_volte
case.ta_steps = {
                'setup'       :    'common_test_case_setup_for_volte',
                'document'    :    'Document about this case',
                'tags'        :     ['VOLTE_PERM'],
                'steps'        :[
                                ['repeat_to_do_voip_call_for_specific_time', '10'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_volte_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_volte',
                        }
all_cases[case.case_name] = case


#Case Volte_call_setup
case = IpaMmlItem()
case.case_name = 'VOLTE_MIX'
case.tm500_version = tm500_version_for_volte
case.tm500_log_types = tm500_log_type_for_volte
case.ta_steps = {
                'setup'       :    'common_test_case_setup_for_volte',
                'document'    :    'Document about this case',
                'tags'        :     ['VOLTE_MIX'],
                'steps'        :[
                                ['pet_ue_attach_for_mix_volte'],
                                ['wait_until_mix_volte_service_is_done'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_volte_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_volte',
                        }
all_cases[case.case_name] = case



#Case Volte_call_drop
case = IpaMmlItem()
case.case_name = 'VOLTE_LOSS_RATIO'
case.tm500_version = tm500_version_for_volte
case.tm500_log_types = tm500_log_type_for_volte
case.ta_steps = {
                'setup'       :    'light_test_case_setup_for_pet',
                'document'    :    'Document about this case',
                'tags'        :     ['VOLTE_LOSS_RATIO'],
                'steps'        :[
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_volte_should_be_ok'],
                            ],
                'teardown'    :'light_test_case_teardown_for_pet',
                        }
all_cases[case.case_name] = case

#Case Volte_call_setup
case = IpaMmlItem()
case.case_name = 'VOLTE_COVERAGE'
case.ta_steps = {
                'setup'       :    'common_test_case_setup_for_volte_coverate',
                'document'    :    'Document about this case',
                'tags'        :     ['VOLTE_COVERAGE'],
                'steps'        :[
                                ['repeat_to_do_voip_call_for_specific_time', '10'],
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_volte_should_be_ok'],
                            ],
                'teardown'    :'common_test_case_teardown_for_volte',
                        }
all_cases[case.case_name] = case



#Throughput for MUE, use UDP
case = IpaMmlItem()
case.case_name = 'THROUGHPUT_MUE_DL'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW', 'L1DLSTATS', 'L1CELLDLOVERVIEW']
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_throughput',
            'document'    :    'Document about this case',
            'tags'        :     ['THROUGHPUT_MUE_DL'],
            'steps'       : [
                            ['pet_ue_attach_for_mue_tput'],
                            ['set_tm500_log_types'],
                            ['wait_until_throughput_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpdl'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_throughput',
                        }
all_cases[case.case_name] = case


#Throughput for MUE, use UDP
case = IpaMmlItem()
case.case_name = 'THROUGHPUT_MUE_UL'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW', 'L1ULSTATS', 'L1CELLULOVERVIEW']
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_throughput',
            'document'    :    'Document about this case',
            'tags'        :     ['THROUGHPUT_MUE_UL'],
            'steps'        :[
                            ['pet_ue_attach_for_mue_tput'],
                            ['set_tm500_log_types'],
                            ['wait_until_throughput_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpul'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_throughput',
                        }
all_cases[case.case_name] = case



#Mix Case for MR
case = IpaMmlItem()
case.case_name = 'MIX_MR'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW', 'L1DLSTATS']
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_mr',
            'document'    :    'Document about this case',
            'tags'        :     ['MIX_MR'],
            'steps'        :[
                            ['pet_ue_attach_for_mix_mr_service'],
                            ['wait_until_mr_service_is_done'],
                            ['get_statistic_info_for_mr_service'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_mr_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_mr',
                        }
all_cases[case.case_name] = case

#Mix Case for MR
case = IpaMmlItem()
case.case_name = 'TRAFFIC_MODEL'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW', 'L1DLSTATS']
case.ta_steps = {
            'setup'       :    'common_suite_setup_for_trafic_model',
            'document'    :    'Document about this case',
            'tags'        :     ['TRAFFIC_MODEL'],
            'steps'        :[
                            ['start_test_scenario'],
                            ['wait_until_traffic_model_service_is_done'],
                            ['get_statistic_info_for_traffic_model'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_traffic_model',
                        }
all_cases[case.case_name] = case

#Mix Case for MR
case = IpaMmlItem()
case.case_name = 'MIX_CAP'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW']
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_mix_cap',
            'document'    :    'Document about this case',
            'tags'        :     ['MIX_CAP'],
            'steps'        :[
                            ['pet_ue_attach_for_mix_cap_service'],
                            ['set_tm500_log_types'],
                            ['wait_until_cap_service_is_done'],
                            ['pet_start_tm500_logging_2'],
                            ['sleep', '300'],
                            ['stop_tm500_logging_and_download_logs_2', 'tmftpul'],
                            ['wait_get_and_deal_voip_result'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_mix_cap_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_mix_cap',
                        }
all_cases[case.case_name] = case

#Case for PRFOA Performace Test Over Artiza
case = IpaMmlItem()
case.case_name = 'PRFOA'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW']
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_prfoa',
            'document'    :    'Document about this case',
            'tags'        :     ['PRFOA'],
            'steps'        :[
                            ['start_service_on_artiza'],
                            ['wait_until_prfoa_service_is_done'],
                            ['get_statistic_info_for_prfoa'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_prfoa_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_prfoa',
                        }
all_cases[case.case_name] = case


case = IpaMmlItem()
case.case_name = 'CPK_MUE_DL_COMBIN'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW', 'L1DLSTATS', 'L1CELLDLOVERVIEW']
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_throughput',
            'document'    :    'Document about this case',
            'tags'        :     ['CPK_MUE_DL_COMBIN'],
            'steps'       : [
                            ['pet_ue_attach_for_mue_tput'],
                            ['set_tm500_log_types'],
                            ['wait_until_throughput_is_ready'],
                            ['pet_start_tm500_logging'],
                            ['start_to_capture_throughput_for_analysis'],
                            ['stop_tm500_logging_and_download_logs', 'tmftpdl'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_throughput_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_throughput',
                        }
all_cases[case.case_name] = case

#Mix Case for MR
case = IpaMmlItem()
case.case_name = 'MIX_STA'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW']
case.ta_steps = {
            'setup'       :    'common_test_case_setup_for_mix_cap',
            'document'    :    'Document about this case',
            'tags'        :     ['MIX_STA'],
            'steps'        :[
                            ['pet_ue_attach_for_mix_cap_service'],
                            ['set_tm500_log_types'],
                            ['wait_until_mix_sta_is_done'],
                            ['check_each_kpi_and_verify_it_is_acceptable'],
                            ['common_check_for_mix_sta_should_be_ok'],
                        ],
            'teardown'    :'common_test_case_teardown_for_mix_cap',
                        }
all_cases[case.case_name] = case


#case for placeholder: this case does not run, just report result of last case.
case = IpaMmlItem()
case.case_name = 'LIGHT_CASE'
case.tm500_version = tm500_version_for_throughput
case.tm500_log_types = ['SYSOVERVIEW']
case.ta_steps = {
            'setup'       :    'light_test_case_setup_for_pet',
            'document'    :    'Document about this case',
            'tags'        :     ['LIGHT_CASE'],
            'steps'       :[
                                ['check_each_kpi_and_verify_it_is_acceptable'],
                                ['common_check_for_pet_should_be_ok'],
                            ],
            'teardown'    :     'light_test_case_teardown_for_pet',
                        }
all_cases[case.case_name] = case


if __name__ == '__main__':
    # import sys, os
    pass
