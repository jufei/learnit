#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

if len(sys.argv) >=2:
    filelist = sys.argv[1:]
    print filelist
else:
    lines = [x for x in os.popen('svn st ./*.py |grep M').readlines() if not 'grep' in x]
    filelist = [x.splitlines()[0].split()[-1] for x in lines]

cmd = 'svn ci -m "Develop" '+' '.join(filelist)
print cmd
os.system(cmd)

upfiles = ['/home/work/tacase/Resource/'+filename for filename in filelist]
cmd = 'svn up '+' '.join(upfiles)
print cmd
os.system(cmd)

print 'sync Done'