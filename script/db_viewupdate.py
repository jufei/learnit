import os, sys
import MySQLdb
from petbase import *

fieldinfo = None
scenarios = None
team = 'PET1'
check_fields = []
viewname = 'vj_tblcase'

from pet_db import getfielddict
fieldinfo = getfielddict()
# def getfielddict():
#     global fieldinfo
#     import copy
#     from pet_db import get_table_content
#     fieldinfo = get_table_content('tblcasedict')
#     basefieldinfo = fieldinfo[:]
#     for prefix in ['ms_', 'sp_', 'ss_']:
#         for field in basefieldinfo:
#             newfield = copy.deepcopy(field)
#             newfield.db_fieldname = prefix+field.db_fieldname
#             newfield.show_fieldname = prefix.replace('_', ' ').upper() + field.show_fieldname
#             fieldinfo.append(newfield)
#     print len(fieldinfo)

def create_view_for_case():
    global fieldinfo
    global viewname

    from pet_db import dba
    db = dba()
    db.setup()
    # fieldinfo = db.get_table_content('tblcase_fieldbook')
    sql = 'create or replace view %s as ' %(viewname)
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
    sql = sql[:-2]
    sql += '\nfrom tblallcase;'
    # print fieldinfo
    print sql
    db.cursor.execute(sql)
    db.cursor.execute('commit;')


getfielddict()
create_view_for_case()