from petbase import *
from pet_pc_c import c_control_pc

class c_pet_filezilla_server(object):
    def __init__(self, tm500):
        self.tm500 = tm500
        self.logger = tm500.logger

    def download_config_file(self):
        from ftp_lib import download_from_ftp_to_local, upload_to_ftp_from_local
        if has_attr(self.tm500.config, 'filezilla_path'):
            if self.tm500.config.filezilla_path:
                self.url = 'ftp://%s/%s/FileZilla Server.xml' %(self.tm500.config.tm500_control_pc_lab, self.tm500.config.filezilla_path)
        else:
            self.url = 'ftp://%s//Program Files/FileZilla Server/FileZilla Server.xml' %(self.tm500.config.tm500_control_pc_lab)
        self.logger.info(self.url)
        self.local_config_file = '/tmp/ftpserver.xml'
        download_from_ftp_to_local(url, self.local_config_file, 'bin', 'filec', 'filec')

    def check_filezilla_working_version(self):
        def _get_version(dire):
            import re
            return re.findall(r'LTE[^\\/]*', dire)[0]

        self.download_config_file()
        app_dire = self.tm500.get_tm500_app_path()
        target_version = _get_version(app_dire)
        self.logger.info('Target Version: ' + target_version)
        from lxml import etree
        tree = etree.parse(self.local_config_file)
        user = tree.xpath('//User[@Name="tm500"]')[0]
        homes = user.xpath('.//Option[@Name="IsHome"]')
        need_modified = False
        working_dire = [home.getparent().get('Dir') for home in homes if home.text == '1'][0]
        need_modified = _get_version(working_dire) <> target_version
        if need_modified:
            self.logger.info('Need Modify filezilla server config')
            for ahome in homes:
                if  _get_version(ahome.getparent().get('Dir')) == target_version:
                    ahome.text = '1'
                else:
                    ahome.text = '0'
            tree.write(self.local_config_file)
            upload_to_ftp_from_local(self.url, self.local_config_file, 'bin', 'filec', 'filec')
        return need_modified

    def setup(self):
        need_reboot = self.check_filezilla_working_version()
        if need_reboot:
            file_zilla_exe_path = "C:\\Program Files\\FileZilla Server\\FileZilla server.exe"
            self.tm500.conn_pc.execute_command('\"%s\" /stop' % file_zilla_exe_path)
            time.sleep(5)
            self.tm500.conn_pc.execute_command('\"%s\" /start' % file_zilla_exe_path)

class c_pet_tma(object):
    def __init__(self, tm500):
        self.tm500 = tm500
        self.logger = tm500.logger

    def start_tma(self):
        connect_to_tm500_control_pc()
        version = 'TM500_APPLICATION_%s_VERSION_DIR' %(gv.case.curr_case.tm500_version)
        tm500_version_dir = self.tm500.get_tm500_app_path()
        tmapath = tm500_version_dir.replace('"', '') + 'Test Mobile Application\\\\TMA.exe'
        client = r'C:\\Python27\\lib\\site-packages\\BtsShell\\resources\\tools\\Server_Client\\client.exe'
        cmd  = r'"%s" localhost %s /u \\"Default User\\" /c y /p 5003 /a n\r\n' %(client, tmapath)
        self.tm500.conn_pc.connect()
        connections.execute_shell_command_bare(cmd)
        time.sleep(5)
        connections.execute_shell_command_bare('\x03')
        self.tm500.conn_pc.wait_until_port_is_listening('5003', '40')

class c_pet_tm500(IpaMmlItem):
    def __init__(self, id):
        self.id = id
        self.conn_pc = None
        self.tma = None
        self.conn_shenick = None
        self.case = None
        self.logger = logging.getLogger(__file__)

        self.read_config()
        self.re_organize_config()
        self.filezilla_server = c_pet_filezilla_server(self)

    def _get_source_dire(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        return os.sep.join(curr_path.split(os.sep) + ['config', 'tm500'])

    def read_config(self):
        tm500path = self._get_source_dire()
        import sys, importlib
        sys.path.append(tm500path)
        model = importlib.import_module('tm500_%s'%(self.id))
        tm500config = IpaMmlItem()
        for key in model.TOOLS_VAR:
            setattr(tm500config, key.lower(), model.TOOLS_VAR[key])
        self.config = tm500config

        self.conn_pc = c_control_pc(self.config.tm500_control_pc_lab, '23',
        self.config.tm500_control_pc_username, self.config.tm500_control_pc_password)


    def config_shenick_group_with_case(self, case):
        self.config.shenick_volte_group_name = 'TA_VOLTE_IMS_FTP'
        if case.codec.strip():
           self.config.shenick_volte_group_name += '_' + case.codec.upper()
        if hasattr(case, 'volte_load'):
            if case.volte_load.strip():
                self.config.shenick_volte_group_name = 'TA_VOLTE_IMS_LOAD'
        if case.case_type == 'VOLTE_CAP':
            self.config.shenick_volte_group_name = 'TA_VOLTE_IMS_FTP_WB2385'
        if case.case_type == 'MIX_MR':
            self.config.shenick_volte_group_name = 'TA_Mixed_UDP_FTP'
        if case.case_type.strip().upper() in ['THROUGHPUT_MUE_UL', 'THROUGHPUT_MUE_DL']:
            self.config.shenick_volte_group_name = 'TA_MUE_UL'

    def re_organize_config(self):
        pass

    def setup(self):
        self.conn_pc.setup()

    def teardown(self):
        self.conn_pc.teardown()

    def attach_to_case(self, case):
        self.case = case

    def get_tm500_app_path(self):
        return getattr(self.config, 'tm500_application_%s_version_dir' %(self.case.tm500_version.lower()))


if __name__ == '__main__':
    from pet_case_c import c_pet_case
    case = c_pet_case('304645')

    tm500 = c_pet_tm500('229')
    print tm500
    tm500.attach_to_case(case)
    tm500.filezilla_server.download_config_file()
    print tm500.filezilla_server.compare_filezilla_working_version()
    # tm500.setup()
    # tm500.teardown()


