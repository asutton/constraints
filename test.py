#!/usr/bin/env python3

from constr import *

import sys

f = open(sys.argv[1])
s = f.read()
c = parse(s)
# print(f"BEFORE: {c}")
d = dnf(c)
# print(f"DNF:    {d}")

app = approx(c)
act = actual(d)
# print(f"APPROX: {app}")
# print(f"ACTUAL: {act}")

if app != act:
  sys.stderr.write(f"* FAILED: {sys.argv[1]} (got {app}, expected {act})\n")
