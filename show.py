#!/usr/bin/env python3

from constr import *

import sys
import os

f = open(sys.argv[1])
s = f.read()
e = parse(s)

# Generate a dot file for the expression.
dot(e, open("expr.dot", "w"))

# Generate a dot file for the DNF of the expression.
dot(dnf(e), open("dnf.dot", "w"))

# Generate a dot file for the CNF of the expression.
dot(cnf(e), open("cnf.dot", "w"))

os.system("dot -Tpdf -o expr.pdf expr.dot")
os.system("dot -Tpdf -o dnf.pdf dnf.dot")
os.system("dot -Tpdf -o cnf.pdf cnf.dot")
