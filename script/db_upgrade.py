import os, sys
import MySQLdb
from petbase import *

fieldinfo = None
scenarios = None
team = 'PET1'
check_fields = []

def get_case_desc(caseid, team):
    global fieldinfo
    import pettool, petcasebase
    from pet_db import get_table_content
    gv.case = IpaMmlItem()
    gv.team = team
    gv.case.curr_case = pettool.get_case_config(caseid)
    petcasebase.re_organize_case()
    case = gv.case.curr_case
    print case

    case.sp_scf_file = case.slave_scf_file

    # fieldinfo = get_table_content('tblcasedict')
    groups = list(set([x.groupname for x in fieldinfo]))
    groups.sort()
    lines = []
    # print case
    groups = ['Basic', 'Scenario', 'BTS', 'Manual Ratio', 'VOLTE', 'Performance', 'Mixed Capacity']
    for group in groups:
        fields = [x for x in fieldinfo if x.groupname == group]
        if fields:
            subs = []
            fieldnames = [x.db_fieldname for x in fields]
            fieldnames.sort()
            vip_fields = ['case_name', 'releaseno', 'owner', 'team', 'domain', 'case_type'] if group == 'Basic' else []
            vip_fields = ['uldl', 'ssf', 'tm', 'band'] if group == 'Scenario' else vip_fields
            vip_fields += [x for x in fieldnames if x not in vip_fields]
            fieldnames = vip_fields[:]
            for fieldname in fieldnames:
                field = [x for x in fields if x.db_fieldname == fieldname][0]
                if not hasattr(case, fieldname):
                    continue

                fname = field.show_fieldname.ljust(40)
                value = str(getattr(gv.case.curr_case, fieldname)).strip()
                default = field.default_value.upper()
                if field.field_type.upper() == 'Boolean'.upper():
                    value = True if  value.upper() in ['1', 'Y', 'YES', 'TRUE'] else False
                    if value:
                        if default =='OFF':
                            value = 'ON'
                        elif default == 'FALSE':
                            value = 'TRUE'
                        elif default == 'NO':
                            value = 'YES'
                        elif default in ['ON', 'TRUE', 'YES']:
                            value = field.default_value.upper()
                    else:
                        if default =='ON':
                            value = 'OFF'
                        elif default == 'TRUE':
                            value = 'FALSE'
                        elif default == 'YES':
                            value = 'NO'
                        elif default in ['OFF', 'FALSE', 'NO']:
                            value = field.default_value.upper()
                if fieldname == 'kpi':
                    value = value.replace(';kpi_cpuload:70', '').replace(';kpi_duration:60.00', '').replace('kpi_cap:20;', '')
                if fieldname == 'band':
                    value = '-'.join([x+'M' for x in value.upper().replace('M', '').split('-')])
                if fieldname == 'tm':
                    value = '-'.join(['TM'+x for x in value.upper().replace('TM', '').split('-')])
                if '\n' in str(value):
                    value = '\n'+value+'\n'
                    value = '{{%s}}' %('\n'.join([line.rjust(60) for line in value.splitlines()]))
                    # value = '{{%s}}' %(value)

                if field.db_fieldname.lower() not in ['ssf', 'uldl', 'scf_file', 'tm', 'tm500_version', 'team', 'releaseno']  and value.upper() == str(field.default_value.upper()).strip():
                    pass
                else:
                    subs.append('%s =  %s' %(fname, value))
            if subs:
                subs = ['[%s]' %(group)] + subs + ['\n']
                lines += subs
    lines = '\n'.join(lines).replace('\n\n', '\n').splitlines()
    # for line in lines:
    #     print line
    return lines
    # print fieldinfo

def parse_config_to_json(lines):
    global fieldinfo
    from pet_db import dba
    db = dba()
    db.setup()

    item = {}
    unknown_field_list = []
    lines = [x.strip() for x in lines]
    lines = [x for x in lines if not x.startswith('[')]
    lines = [x for x in lines if not x.startswith('#')]
    lines = [x for x in lines if x.replace('\n', '').strip()]
    all_text= '\n'.join(lines)+'\n'

    mode = 'find_var'
    fieldname, fieldvalue, fieldtype = '', '', ''
    invar = False
    while all_text:
        c = all_text[0]
        if c == '=':
            mode = 'find_value'
        elif c=='\n':
            if invar:
                fieldvalue += c
            else:
                fieldname = fieldname.lower().strip()
                field = [x for x in fieldinfo if x.show_fieldname.lower().strip().replace(' ', '_') == fieldname.strip().lower().strip().replace(' ', '_').strip()]
                if field:
                    db_fieldname = field[0].db_fieldname
                    fieldtype = field[0].field_type
                else:
                    raise Exception, 'Could not find the field for :' + fieldname.lower().replace(' ', '_').strip()
                if db_fieldname == 'band':
                    fieldvalue = fieldvalue.replace('M','')
                if fieldtype == 'string':
                    item[db_fieldname.strip()] = fieldvalue.strip()
                elif fieldtype == 'integer':
                    item[db_fieldname.strip()] = int(fieldvalue.strip())
                elif fieldtype == 'Boolean' and fieldvalue.strip() in ['ON']:
                    item[db_fieldname.strip()] = 1
                elif fieldtype == 'Boolean' and fieldvalue.strip() in ['OFF']:
                    item[db_fieldname.strip()] = 0
                else:
                    item[db_fieldname.strip()] = fieldvalue.strip()
                fieldname, fieldvalue, fieldtype = '', '', ''
                mode = 'find_var'
        elif c=='{':
            invar = True
        elif c=='}':
            invar = False
        else:
            if mode == 'find_var':

                fieldname += c
            else:
                fieldvalue += c
        all_text = all_text[1:]
    return item

def create_view_for_case():
    global fieldinfo
    from pet_db import dba
    db = dba()
    db.setup()
    # fieldinfo = db.get_table_content('tblcase_fieldbook')
    sql = 'create or replace view vj_tblcase as '
    sql += '\nselect id as id, '

    for field in fieldinfo:
        if field.field_type.lower() == 'string':
            default = '"%s"' %(field.default_value)
            field_type = 'char'
        elif field.field_type.lower() == 'boolean':
            if field.default_value.upper() in ['TRUE', 'YES', 'Y', 'ON']:
                default = '1'
            else:
                default = '0'
            field_type = 'UNSIGNED'
        elif field.field_type.lower() == 'integer':
            default = int(field.default_value) if str(field.default_value).strip() else '0'
            field_type = 'UNSIGNED'
        else:
            default = field.default_value
        if field.db_fieldname == 'mts_scenario':
            sql += '\n CAST(IFNULL(JSON_EXTRACT(caseinfo, "$.%s"), %s) as %s) as %s,' %(field.db_fieldname, default, field_type, field.db_fieldname)
        elif field.field_type.lower() == 'string':
            c = 'IFNULL(JSON_EXTRACT(caseinfo, "$.%s"), %s) ' %(field.db_fieldname, default)
            c = 'REPLACE(' + c + ', ' + "'" + '"' + "'" +', "") '
            c = '\nCAST(%s as CHAR) as %s,' %(c, field.db_fieldname)
            sql += c
        else:
            c = '\nCAST(IFNULL(JSON_EXTRACT(caseinfo, "$.%s"), %s) as %s) as %s, ' %(field.db_fieldname, default, field_type, field.db_fieldname)
            # c = '\n REPLACE(' + c + ', ' + "'" + '"' + "'" +', "") as ' + field.db_fieldname + ','
            sql += c
    sql = sql[:-1]
    sql += '\nfrom tblallcase;'
    # print fieldinfo
    print sql
    return sql

def update_case_table():
    global fieldinfo
    from pet_db import dba
    gv.adb = dba()
    gv.adb.setup()

    #Remove all data
    # gv.adb.cursor.execute('delete from tblallcase;')
    # gv.adb.cursor.execute('commit;')

    # #Move PET1 case
    # gv.adb.cursor.execute('select qc_test_instance_id from tblcase')
    # record = gv.adb.cursor.fetchall()
    # for caseid in record:
    #     gv.logger.info('Running:  ' + str(caseid[0]))
    #     lines = get_case_desc(str(int(caseid[0])), 'PET1')
    #     sql = 'insert into tblallcase (casedesc) values ("%s");' %('\n'.join(lines).replace('\\', '\\\\'))
    #     print sql
    #     gv.adb.cursor.execute(sql)
    # gv.adb.cursor.execute('commit;')

    # # #Move Pet2 Case
    # gv.adb.cursor.execute('select qc_test_instance_id from tblcasepet2')
    # record = gv.adb.cursor.fetchall()
    # for caseid in record:
    #     gv.logger.info('Running:  ' + str(caseid[0]))
    #     lines = get_case_desc(str(int(caseid[0])), 'PET2')
    #     sql = 'insert into tblallcase (casedesc) values ("%s");' %('\n'.join(lines).replace('"', r'\"'))
    #     print sql
    #     gv.adb.cursor.execute(sql)
    # gv.adb.cursor.execute('commit;')


    #Update case info field
    gv.adb.cursor.execute('select id, team from vj_tblcase ')
    records = gv.adb.cursor.fetchall()
    print records[0]
    for record in records:
        # result = parse_config_to_json(record[6].splitlines())
        # print result
        # sql = 'update tblallcase  set caseinfo=\n'
        # sql += '    JSON_MERGE('
        # for fieldname in result:
        #     field = [x for x in fieldinfo if x.db_fieldname.lower().replace(' ', '_').strip() == fieldname.lower()][0]
        #     db_fieldname = field.db_fieldname
        #     if field.field_type.lower() == 'string':
        #         value = result[fieldname].replace('"', r'\"')
        #         if '_path' in field.db_fieldname:
        #             value = value.replace('\\', '\\\\')
        #         value = '"%s"' %(value)
        #     elif field.field_type == 'integer':
        #         value = int(result[fieldname])
        #     elif field.field_type.lower() == 'boolean':
        #         value = 1 if str(result[fieldname]).upper() in ['ON','TRUE', 'YES', 'Y', '1'] else 0
        #     else:
        #         raise Exception, 'Unknown field type: '+ field.field_type

        #     sql += '\n        JSON_OBJECT("%s", %s),' %(db_fieldname, value)
        # sql = sql[:-1] + ')\n where id=%s;' %(str(record[0]))


        # print sql
        # gv.adb.cursor.execute(sql)

        # sql =  'update tblallcase set qc_test_instance_id=%s, case_name="%s", owner="%s", case_type="%s", releaseno="%s" where id=%s;' %(
        #     result['qc_test_instance_id'], result['case_name'], result['owner'], result['case_type'], result['releaseno'],
        #     str(record[0])
        #     )
        # print sql
        # gv.adb.cursor.execute(sql)

        # print result
        sql =  'update tblallcase set team="%s" where id=%s;' %(
            str(record[1]),
            str(record[0])
            )
        print sql
        # break
        gv.adb.cursor.execute(sql)

    gv.adb.cursor.execute('commit;')


    # sql = create_view_for_case()
    # gv.adb.cursor.execute(sql)
    # gv.adb.cursor.execute('commit;')


def case_compare(caseid):
    global fieldinfo
    from pettool import get_case_config_new, get_case_config
    newcase = get_case_config_new(caseid)

    case = get_case_config(caseid)
    gv.case.curr_case = case
    from petcasebase import re_organize_case
    re_organize_case()
    oldcase = gv.case.curr_case
    diff = []
    for attr in [x for x in dir(newcase) if not x.startswith('_') and x not in ['id', 'kpi']]:
        if hasattr(oldcase, attr):
            # print attr
            newvalue = getattr(newcase, attr)
            oldvalue = getattr(oldcase, attr)
            field = [x for x in fieldinfo if x.db_fieldname == attr][0]
            if field.field_type.lower() == 'boolean':
                oldvalue = False if oldvalue=='' else oldvalue
                oldvalue = False if oldvalue=='0' else oldvalue
            if field.field_type.lower() == 'integer':
                oldvalue = int(oldvalue)
            if field.field_type.lower() == 'string':
                if '\n' in oldvalue:
                    oldvalue = oldvalue.splitlines()
                if '\n' in newvalue:
                    newvalue = newvalue.splitlines()

            if newvalue <> oldvalue:
                diff.append([attr, newvalue, oldvalue])
    if diff:
        print diff
        raise Exception, 'Diff found for case: '+ str(newcase.qc_test_instance_id)
    else:
        print 'Match Succeed.'

def check_match_all_case(team = 'PET1'):
    gv.team = team
    from pet_db import dba
    gv.adb = dba()
    gv.adb.setup()
    if team == 'PET1':
        gv.adb.cursor.execute('select qc_test_instance_id from tblcase where qc_test_instance_id>0 order by qc_test_instance_id')
    # gv.adb.cursor.execute('select qc_test_instance_id from tblcase where qc_test_instance_id=603438;')
    else:
        gv.adb.cursor.execute('select qc_test_instance_id from tblcasepet2 order by qc_test_instance_id')
    record = gv.adb.cursor.fetchall()
    for caseid in record:
        caseid = str(int(caseid[0]))
        print 'Comparing....', caseid
        case_compare(caseid)


def update_btsfiles():
    from pet_db import dba
    gv.adb = dba()
    gv.adb.setup()
    gv.adb.cursor.execute('delete from tblbtsfiles;')
    gv.adb.cursor.execute('commit;')
    root = '/home/work/tacase/Resource/config/bts'
    for dire in os.listdir(root):
        btsid = dire.replace('BTS', '')
        path = os.sep.join([root, dire])
        for filename in os.listdir(path):
            if not '.pyc' in filename:
                filename = os.sep.join([path, filename])
                basename = os.path.basename(filename)
                basename = 'config/bts/BTS%s/%s' %(btsid, basename)
                sql = 'insert into tblbtsfiles (btsid, filename, filecontent) values (%s, "%s", LOAD_FILE("%s"));' %(btsid, basename, filename)
                print sql
                gv.adb.cursor.execute(sql)
    gv.adb.cursor.execute('commit;')




if __name__ == '__main__':
    # global fieldinfo
    gv.team = 'PET1'
    from pettool import get_case_config_new
    from pet_db import getfielddict
    fieldinfo = getfielddict()
    # print 'XXXXXXXXXXXx'
    # print fieldinfo
    # print get_case_config('305581')
    # update_case_table()
    # check_match_all_case('PET1')
    # check_match_all_case('PET2')
    # update_btsfiles()
    # create_view_for_case()
    print get_case_config_new('603300')

    # get_case_desc('564558', 'PET1')
    # print get_case_config_new('564558')
    # case_compare('564558')