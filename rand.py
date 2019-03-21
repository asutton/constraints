from constr import *

import random
from datetime import datetime

random.seed(datetime.now())

deepest = 5
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

c = gen()
print(c)

print(dnf(c))
print(clauses(c))
