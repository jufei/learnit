#!/usr/bin/python

import os,sys

cmd = 'ps -efww |grep pppoe-connect'

print cmd
lines = [x for x in os.popen(cmd).readlines() if not 'grep' in x]
if len(lines) == 0:
    print 'No ppppoe found'
    sys.exit()
print lines[0]
