import os
import pet_scf_base_c
from pet_scf_base_c import scf_parameters
import re
from inspect import getsource
from pet_scf_manager import *

from pet_db import dba

scf_class = pet_scf_base_c.c_pet_scf_base

sub_fun_str = r'(self._[\s\S]*\(bts)'

def get_function_code(funname):
    if hasattr(scf_class, funname):
        output = []
        fun_obj = getattr(pet_scf_base_c.c_pet_scf_base, funname)
        lines = getsource(fun_obj).splitlines() + ['']
        for line in lines:
            subfuns = re.findall(sub_fun_str, line)
            for subfun in subfuns:
                subfun_name = subfun.split('.')[-1].split('(')[0]
                output += get_function_code(subfun_name)
        # output += ['##Function: %s' %(funname)] + lines
        output += lines
        return output
    else:
        raise Exception, 'Could not find the funcion: [%s]' %(funname)

def get_domain_code(btstype, domain):
    flag = '%s_%s' %(btstype, domain)
    param_list = scf_param_map[flag]
    param_list.sort()
    output = []
    for param in param_list:
        funname = scf_parameters[param]
        output += get_function_code(funname)
    return output


def update_db_for_code():
    db = dba()
    db.connect()
    db.run_sql('delete from tblscfcode;')
    scf_parameters['beforming']  = 'get_changes_for_beforming'
    scf_parameters['pipe']       = 'get_changes_for_pipe'
    scf_parameters['csi_config'] = 'get_changes_for_csi_config_info'
    for btstype in ['TDD', 'FDD']:
        for domain in ['CPK', 'CAP', 'TR', 'MR', 'VOLTE', 'PRF']:
            flag = '%s_%s' %(btstype, domain)
            param_list = scf_param_map[flag]
            param_list.append
            param_list += ['beforming', 'pipe', 'csi_config']
            param_list.sort()
            for param in param_list:
                funname = scf_parameters[param]
                code =  get_function_code(funname)
                code = '\n'.join(code)
                code = code.replace('"', '\\"')
                sql = 'insert into tblscfcode (btstype, domain, scf_param, code) values("%s", "%s", "%s", "%s");' %(
                    btstype,
                    domain,
                    param,
                    code,
                    )
                db.run_sql(sql)

    db.run_sql('commit;')
    db.disconnect()


# lines = get_domain_code('TDD', 'CPK')
# for line in lines:
#     print line

update_db_for_code()