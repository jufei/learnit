from ute_admin import ute_admin
import os
for key in ['http_proxy', 'https_proxy']:
    if os.environ.has_key(key):
        del os.environ[key]
admin = ute_admin()
btsip = '10.69.67.140'
btsip = '10.69.66.166'
btsid = '623'
planid = '3221225472'
scf_file = '/home/work/temp/som_a.xml'

alias = btsid
print 'Before setup'
try:
    admin.setup_admin(bts_host = btsip, alias=btsid, bts_port=9002, use_ssl=False, timeout=90)
    print 'Setup OK'
    # admin.collect_snapshot('snapss.zip', alias=btsid)
    # admin.collect_snapshot('/home/work/temp/scf/snpa.zip',  alias=btsid)
    # admin.collect_scf('/home/work/temp/som_a.xml',  alias=btsid)
    admin.perform_commissioning(plan_id=planid, bts_id=btsid, scf_file=scf_file, timeout=300,
        skip_parameter_relation_errors=True,
        should_activate=False,
        alias=alias)
    # admin.activate_plan(plan_id = planid, alias=alias)
    print 'in teardown'
finally:
    admin.teardown_admin(alias=btsid)