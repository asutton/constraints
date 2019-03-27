#!/usr/bin/env python3

from constr import *

import sys
import os
import random
from datetime import datetime

random.seed(datetime.now())

deepest = 4
count = 0

def atom():
  global count

  count += 1
  return Atom("p" + str(count))

def op(cd, depth):
  global deepest

  if depth >= deepest:
    return atom()

  return cd(gen(depth + 1), gen(depth + 1))

def gen(depth = 0):
  # FIXME: We should probably give these weighted probabilities.
  n = random.randint(0, 2)
  if n == 0:
    return atom()
  elif n == 1:
    return op(Conj, depth)
  else:
    return op(Disj, depth)


def next_file():
  files = os.listdir("input")
  last = max(list(map(lambda x: int(x.split('.')[0]), files)))
  return last + 1

# Get the next file number to generate.
next = next_file()

for i in range(1, 100):
  count = 0
  c = gen()
  print(f"IN: {c}")
  d = dnf(c)
  print(f"DNF:    {d}")

  app = approx_dnf(c)
  act = actual_dnf(d)

  print(f"APPROX: {app}")
  print(f"ACTUAL: {act}")

  if app != act:
    sys.stderr.write(f"* FAILED: {c}\n")
    sys.stderr.write(f"- saved as {next}.txt\n")
    f = open(f"input/{next}.txt", "w")
    f.write(f"{str(c)}\n")
    f.close()
    next += 1
