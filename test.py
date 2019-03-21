from constr import *

import sys

f = open(sys.argv[1])
s = f.read()
c = parse(s)
print(c)
# print(repr(c))

d = dnf(c)
print(d)
print(clauses(c))
