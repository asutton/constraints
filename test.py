#!/usr/bin/env python3

from constr import *

import sys

f = open(sys.argv[1])
s = f.read()

e = parse(s)

# Show the DNF and CNF rewrites.
print(f"INPUT: {e}")

d = dnf(e)
print(f"DNF:    {d}")
dapp = approx_dnf(d)
print(f"APPROX DNF: {dapp}")
dact = actual_dnf(d)
print(f"ACTUAL DNF: {dact}")

c = cnf(e)
print(f"CNF:    {c}")
capp = approx_cnf(c)
print(f"APPROX CNF: {capp}")
cact = actual_cnf(c)
print(f"ACTUAL CNF: {cact}")

if dapp != dact:
  sys.stderr.write(f"* FAILED DNF: {sys.argv[1]} (got {dapp}, expected {dact})\n")
if capp != cact:
  sys.stderr.write(f"* FAILED CNF: {sys.argv[1]} (got {capp}, expected {cact})\n")
