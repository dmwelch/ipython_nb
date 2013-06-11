# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Subprocess

# <codecell>

from subprocess import *
# call(['pwd'])
p1 = Popen(["ls"], stdout=PIPE)
p2 = Popen(["grep", "mat"], stdin=p1.stdout, stdout=PIPE)
# print p1.stdout.readlines() ### BUG: Weird behavior when this is uncommented...
p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
output, outerr = p2.communicate()
p2.stdout.close()
print output, outerr
# q = Popen('find . -type f -name *.1D', stdout=PIPE, sterr=STDOUT)
# print q.stout.readlines()

# <headingcell level=1>

# Argparse

# <codecell>

import argparse
temp = argparse.ArgumentParser()
temp.add_argument('--foo')
kwds = vars(temp.parse_args(['--foo', 'BAR']))

# <headingcell level=1>

#     *args and **kwds

# <codecell>

def test(*args, **kwds):
    print 'args'
    print args
    print 'kwds:'
    print kwds
    
test(**kwds)

# <headingcell level=1>

# tempfile

# <codecell>

import tempfile
test = tempfile.NamedTemporaryFile()
print test.name
with open(test.name, 'w') as fid:
    fid.write('This is a test')
with open(test.name, 'r') as fid:
    print fid.readlines()

# <codecell>


