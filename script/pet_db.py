import os, sys
import MySQLdb
from petbase import *

db_server = '10.69.64.113'
db_server = '10.69.2.134'

class db_config(object):
    def __init__(self, ip, port, username, password, dbname):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname

class dba(object):
    def __init__(self):
        self.config = db_config(db_server, 3306, 'root', 'root', 'petdb')
        self.db = None

    def connect(self):
        if not self.db:
            self.db = MySQLdb.connect(host=self.config.ip, user=self.config.username,
                        passwd=self.config.password, db=self.config.dbname, port=self.config.port)
            self.cursor = self.db.cursor()

    def disconnect(self):
        self.db.close()
        self.cursor = None

    def run_sql(self, sql):
        print sql
        self.cursor.execute(sql)

    def setup(self):
        self.connect()

    def teardown(self):
        self.disconnect()

    def get_table_fields(self, tablename):
        self.cursor.execute('select * from %s where 1=0' %(tablename))
        return [x[0] for x in self.cursor.description]

    def get_table_structure(self, tablename):
        self.cursor.execute('desc '+tablename)
        return self.cursor.fetchall()

    def get_table_content(self, tablename = '', condition = ''):
        gv.logger.info('Retrieve data from table: ' + tablename)
        fields = self.get_table_fields(tablename)
        self.cursor.execute('select * from  %s %s' %(tablename, condition))
        result = []
        from pet_ipalib import IpaMmlItem
        for record in self.cursor.fetchall():
            p = IpaMmlItem()
            for i in range(len(fields)):
                if record[i] <> None:
                    setattr(p, fields[i].lower(), str(record[i]))
                else:
                    setattr(p, fields[i].lower(), '')
            result.append(p)
        return result


    def convert_database(self, tablename):
        import xlrd
        bk = xlrd.open_workbook('/root/work/tacase/Resource/config/case/database.xlsx')
        shxrange = range(bk.nsheets)
        sh = bk.sheet_by_name('cases')
        nrows= sh.nrows
        titles = sh.row_values(0)
        info = []
        for i in range(1, nrows):
            line = ['%s' % (x) for x in sh.row_values(i)]
            acase = {}
            if line[0].strip():
                for j in range(len(titles)):
                    if titles[j].strip():
                        acase[titles[j].lower().strip()] = line[j].replace('.0','').strip()
            info.append(acase)

def getfielddict():
    import copy
    fieldinfo = get_table_content('tblcasedict')
    basefieldinfo = fieldinfo[:]
    for prefix in ['ms_', 'sp_', 'ss_']:
        for field in [x for x in basefieldinfo if x.scf_related=='Y']:
            newfield = copy.deepcopy(field)
            newfield.db_fieldname = prefix+field.db_fieldname
            newfield.show_fieldname = prefix.replace('_', ' ').upper() + field.show_fieldname
            fieldinfo.append(newfield)
    return fieldinfo

def initlize_db():
    gv.adb = dba()
    gv.adb.setup()

def finalize_db():
    gv.adb.teardown()
    gv.adb = None

def get_table_content(tablename = '', condition = ''):
    adb = dba()
    adb.setup()
    result = adb.get_table_content(tablename, condition)
    adb.teardown()
    return result

def get_table_structure(tablename):
    adb = dba()
    adb.setup()
    result = adb.get_table_structure(tablename)
    adb.teardown()
    return result

def get_scenario_check_fields():
    structure = get_table_structure('tblscenario')
    return [field[0] for field in structure if 'tinyint' in field[1]]

def get_case_check_fields():
    structure = get_table_structure('tblscenario')
    structure += get_table_structure('tblcase')
    structure += get_table_structure('tblcasepet2')
    structure = list(set(structure))
    structure.sort()
    return [field[0] for field in structure if 'tinyint' in field[1]]

def get_scenario_config(obj):
    return obj.scenariostr

def read_scenario_db():
    scenarios = get_table_content('tblscenario')
    check_fields = get_scenario_check_fields()
    for i in range(len(scenarios)):
        scenario =scenarios[i]
        scenario.seq = i
        for field in check_fields:
          value = getattr(scenario, field)
          if str(value) == 'NULL' or str(value) == '0' or str(value) == '':
              setattr(scenario, field, False)
          else:
              setattr(scenario, field, True)
          if field not in ['pipe'] and str(value) == '1':
              setattr(scenario, field, True)
        scenario.master_bts_config = get_scenario_config(scenario)

    # result = IpaMmlDict()
    # for scenario in scenarios:
    #     result[str(scenario.id)] = scenario
    # return result
    return scenarios

def read_all_case_db(team):
    scenarios = read_scenario_db()
    check_fields = get_case_check_fields()
    gv.logger.info('Total Scenario Count: %d' %(len(scenarios)))
    tablename = 'tblcasepet2' if team.upper() == 'PET2' else 'tblcase'
    cases = get_table_content(tablename)
    for case in cases:
        for attr in [x for x in dir(case) if x[0] <> '_']:
            value = str(getattr(case, attr)).strip().upper()
            if value == 'NULL':
                setattr(case, attr, '')
            if attr in check_fields:
                if value in ['NULL', '0', '']:
                    setattr(case, attr, False)
                else:
                    setattr(case, attr, True)

        # if not case.ready:
        #     continue
        scenario = [x for x in scenarios if x.id == case.master_bts_config]
        if scenario:
            for field in dir(scenario[0]):
                if field <> 'id' and field[0] <> '_':
                    setattr(case, field, getattr(scenario[0], field))
            case.mp_scenario = scenario[0]
        else:
            raise Exception, 'Non-exist scenario id for the case: [%s] ' %(case.master_bts_config)

        case.use_ms = False
        if case.master_secondary_scenario:
            case.use_ms = True
            scenario = [x for x in scenarios if x.id == case.master_secondary_scenario]
            if scenario:
                case.ms_scenario = scenario[0]
            else:
                raise Exception, 'Non-exist scenario id for the case: [%s] ' %(case.master_secondary_scenario)

    return cases

def read_all_case_db_new(id):
    case = get_table_content('vj_tblcase', ' where qc_test_instance_id=%s' %(id))
    return case

def testforfile():
    db = dba()
    db.setup()
    db.cursor.execute('select filecontent from tblbtsfiles where id=4;')
    filecontent = db.cursor.fetchall()[0][0]
    with open('/tmp/swconfig.txt', 'w') as f:
        f.write(filecontent)
    # print filecontent


if __name__ == '__main__':
    # dump_to_json_db()
    # create_view_for_case()
    # testforfile()
    # case = read_all_case_db_new('325093')
    # print case
    fields = getfielddict()
    p = [x.db_fieldname for x in fields]
    p.sort()
    print p
    print len(p)
    # gv.adb = dba()
    # gv.adb.setup()
    # gv.adb.cursor.execute('select qc_test_instance_id from tblcase where ready=1 and releaseno="TL17SP"')
    # record = gv.adb.cursor.fetchall()
    # for caseid in record:
    #     # print caseid
    #     print str(int(caseid[0]))
    #     lines = get_case_desc(str(int(caseid[0])))
    #     print parse_config_to_json(lines)
    # lines = get_case_desc('564558')
    # parse_config_to_json(lines)
    # print gv.case.curr_case
    # sheetname = 'rfinfo'
    # adb.teardown()



