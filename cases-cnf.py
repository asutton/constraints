from constr import *

# Counting

def recur_cnf(c, depth):
  # Recursively count clauses in each subtree.
  p1 = approx_cnf_recur(c.lhs, depth + 1)
  p2 = approx_cnf_recur(c.rhs, depth + 1)
  
  # Get the number of nodes in each subtree.
  n1 = p1[0]
  n2 = p2[0]

  # Get the number of distributions in each subtree.
  d1 = p1[1]
  d2 = p2[1]

  return n1, n2, d1, d2

def approx_cnf_disj(c, depth):
  # Matches _ or _; distributes when either LHS or RHS
  # is a conjunction or when both are conjunctions.
  
  n1, n2, d1, d2 = recur_cnf(c, depth)
  lhs = c.lhs
  rhs = c.rhs

  if disj(lhs):
    if disj(rhs):
      if d1 and d2: # Both LHS and RHS are conjunctions.
        return (n1 * n2, True)
      if d1 != d2: # Either LHS or RHS is a conjunction.
        return (n1 + n2, True)
      else: # nNither LHS nor RHS is a conjunction.
        return (0, False)
    if conj(rhs):
      if d1: # LHS and RHS are conjunctions.
        return (n1 * n2, True)
      else: # Only RHS is a conjunction.
        return (n1 + n2, True)
    if atom(rhs):
      if d1: # Only RHS is a conjunction.
        return (n1 + n2, True)
      else: # Neither LHS nor RHS is a conjunction.
        return (0, False)
  
  if conj(lhs):
    if disj(rhs):
      if d2: # Both LHS and RHS are conjunctions.
        return (n1 * n2, True)
      else: # Only LHS is a conjunction.
        return (n1 + n2, True)
    if conj(rhs): # Both LHS and RHS are conjunctions.
      return (n1 * n2, True)
    if atom(rhs): # Only LHS is a conjunction.
      return (n1 + n2, True)

  if atom(lhs):
    if disj(rhs):
      if d2: # Only RHS is a conjunction.
        return (n1 + n2, True)
      else: # Neither LHS nor RHS is a disjunction.
        return (0, False)
    if conj(rhs): # Only RHS is a conjunction
      return (n1 + n2, True)
    if atom(rhs): # Neither LHS nor RHS is a conjunction.
      return (0, False)

  assert False

def approx_cnf_conj(c, depth):
  # Matches _ or _; combines count when both LHS and RHS are conjunctions
  # and also adds to the count when either side is a conjunction.
  # conjunctions of non-conjunctions contribute 2 problems.

  n1, n2, d1, d2 = recur_cnf(c, depth)
  lhs = c.lhs
  rhs = c.rhs
  
  if disj(lhs):
    if disj(rhs):
      if d1 and d2: # Both LHS and RHS are conjunctions.
        return (n1 + n2, d1 or d2)
      if d1 != d2: # Either LHS or RHS is a conjunction.
        return (1 + n1 + n2, d1 or d2)
      else: # Neither LHS nor RHS is a conjunction.
        return (2, False)
    if conj(rhs):
      if d1: # Both LHS and RHS are conjunctions
        return (n1 + n2, d1 or d2)
      else: # Only RHS is a conjunction
        return (1 + n1 + n2, d1 or d2)
    if atom(rhs):
      if d1: # Only RHS is a conjunction
        return (1 + n1 + n2, d1 or d2)
      else: # Neither LHS nor RHS is a conjunction
        return (2, False)

  if conj(lhs):
    if disj(rhs):
      if d2: # Both LHS and RHS are conjunctions.
        return (n1 + n2, d1 or d2)
      else: # Only LHS is a conjunction.
        return (1 + n1 + n2, d1 or d2)
    if conj(rhs): # Both LHS and RHS  are conjunctions
      return (n1 + n2, d1 or d2)
    if atom(rhs): # Only LHS is a conjunction
      return (1 + n1 + n2, d1 or d2)

  if atom(lhs):
    if disj(rhs):
      if d2: # Only RHS is a conjunction
        return (1 + n1 + n2, d1 or d2)
      else: # Neither LHS nor RHS is a conjunction
        return (2, False)
    if conj(rhs): # Only RHS is a conjunction
      return (1 + n1 + n2, d1 or d2)
    if atom(rhs): # Neither LHS nor RHS is a conjunction
      return (2, False)

  assert False

def approx_cnf_atom(c, depth):
    print(f"{2 * depth * ' '}<<< X: {c} -> 0/0")
    return (0, False)  

def approx_cnf_recur(c, depth = 0):
  print(f"{2 * depth * ' '}>>> {c}")

  if type(c) is Atom: # x
    return approx_cnf_atom(c, depth)

  if type(c) is Disj: # _ or _
    return approx_cnf_disj(c, depth)

  if type(c) is Conj: # _ and _
    return approx_cnf_conj(c, depth)

  assert False


def approx_cnf(c):
  # FIXME: This isn't actually an approximation.
  n, d = approx_cnf_recur(c)
  return n if n else 1 # Adjust 0's to 1s


def actual_cnf_recur(c):
  if type(c) is Conj:
    return 1 + actual_cnf_recur(c.lhs) + actual_cnf_recur(c.rhs)
  else:
    return 0

def actual_cnf(c):
  # FIXME: This is not well named.
  return 1 + actual_cnf_recur(c)
