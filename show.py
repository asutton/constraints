#!/usr/bin/env python3

from constr import *

import sys
import os

f = open(sys.argv[1])
s = f.read()
c = parse(s)

# Generate a dot specification of the input
dot(c, open("in.dot", "w"))

d = dnf(c)
dot(d, open("dnf.dot", "w"))

os.system("dot -Tpdf -o in.pdf in.dot")
os.system("dot -Tpdf -o dnf.pdf dnf.dot")
