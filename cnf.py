from constr import *

def dist(c, lhs, rhs, depth):
  # Matches p or q -- we may need to distribute.

  if conj(lhs) and conj(rhs):
    # Matches (a and b) or (p and q)
    r = foil(lhs, rhs, depth)
    # print(f"{2 * depth * ' '}GOT FOIL: {r}")
    return r

  if (conj(lhs)):
    # Matches (a and b) or p
    r = distl(lhs, rhs, depth)
    # print(f"{2 * depth * ' '}GOT DISTL: {r}")
    return r

  if (conj(rhs)):
    # Matches a or (p and q)
    r = distr(lhs, rhs, depth)
    # print(f"{2 * depth * ' '}GOT DISTR: {r}")
    return r

  # No conjunctions to distribute over; just rebuild the term.
  r = Disj(lhs, rhs)
  # print(f"{2 * depth * ' '}GOT DISJ: {r}")
  return r

def distr(lhs, rhs, depth):
  # Matches a or (p and q) -- a distributes over (p and q) to
  # give us (a or p) and (a or q).
  
  # Build (a or p); recursively redistribute as needed.
  c1 = Disj(lhs, rhs.lhs)
  c1 = dist(c1, c1.lhs, c1.rhs, depth + 1)
  
  # Build (a or q); recursively redistribute as needed.
  c2 = Disj(lhs, rhs.rhs)
  c2 = dist(c2, c2.lhs, c2.rhs, depth + 1)

  # Build the conjunction.
  return Conj(c1, c2)

def distl(lhs, rhs, depth):
  # Matches (a and b) or p -- p distributes over (a and b) to
  # give us (a or p) and (b or p).
  
  # Build (a or p); recursively redistribute as needed.
  c1 = Disj(lhs.lhs, rhs)
  c1 = dist(c1, c1.lhs, c1.rhs, depth + 1)

  # Build (b or p); recursively redistribute as needed.
  c2 = Disj(lhs.rhs, rhs)
  c2 = dist(c2, c2.lhs, c2.rhs, depth + 1)

  # Build the conjunction.
  return Conj(c1, c2)

def foil(lhs, rhs, depth):
  # Matches (a or b) and (p or q) -- apply FOIL to produce
  # (a or p) and (a or q) and (b or p) and (b or q).

  # Build (a or p); recursively redistribute as needed.
  f = Disj(lhs.lhs, rhs.lhs)
  f = dist(f, f.lhs, f.rhs, depth + 1)

  # Build (a or q); recursively redistribute as needed.
  o = Disj(lhs.lhs, rhs.rhs)
  o = dist(o, o.lhs, o.rhs, depth + 1)

  # Build (b or p); recursively redistribute as needed.
  i = Disj(lhs.rhs, rhs.lhs)
  i = dist(i, i.lhs, i.rhs, depth + 1)

  # Build (b or q); recursively redistribute as needed.
  l = Disj(lhs.rhs, rhs.rhs)
  l = dist(l, l.lhs, l.rhs, depth + 1)
  
  # Rebuild the constraint, nesting to the left.
  return Conj(Conj(Conj(f, o), i), l)

def cnf(c, depth = 0):
  # print(f"{2 * depth * ' '}CNF: {c}")

  if type(c) is Atom:
    # Matches p -- can't distribute
    # print(f"{2 * depth * ' '}GOT ATOM: {c}")
    return c

  lhs = cnf(c.lhs, depth + 1)
  rhs = cnf(c.rhs, depth + 1)

  if type(c) is Conj:
    # Matches p and q -- no transformation needed.
    # print(f"{2 * depth * ' '}GOT CONJ: {c}")
    return Conj(lhs, rhs)

  if type(c) is Disj:
    # Matches p or q -- need to distribute
    # print(f"{2 * depth * ' '}GOT DISJ: {c}")
    return dist(c, lhs, rhs, depth)

  assert False


# Counting

def recur_dnf(c, depth):
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
  
  n1, n2, d1, d2 = recur_dnf(c, depth)
  lhs = c.lhs
  rhs = c.rhs

  if disj(lhs):
    if (disj(rhs) and d1 and d2) or (conj(rhs) and d1):
      # Both LHS and RHS are conjunctions
      return (n1 * n2, True)
    if (disj(rhs) and (d1 != d2)) or conj(rhs) or (atom(rhs) and d1):
      # Either LHS or RHS are conjunctions
      return (n1 + n2, True)
    if disj(rhs) or atom(rhs):
      # Neither LHS nor RHS are conjunctions
      return (0, False)
    assert False

  if conj(lhs):
    if (disj(rhs) and d2) or conj(rhs):
      # Both LHS and RHS are conjunctions.
      return (n1 * n2, True)
    if disj(rhs) or atom(rhs):
      # Only LHS is a conjunction
      return (n1 + n2, True)
    assert False

  if atom(lhs):
    if (disj(rhs) and d2) or conj(rhs):
      # Only RHS is a conjunction
      return (n1 + n2, True)
    if disj(rhs) or atom(rhs):
      # Neither LHS nor RHS are conjunction
      return (0, False)
    assert False

  assert False

def approx_cnf_conj(c, depth):
  # Matches _ or _; combines count when both LHS and RHS are conjunctions
  # and also adds to the count when either side is a conjunction.
  # conjunctions of non-conjunctions contribute 2 problems.

  n1, n2, d1, d2 = recur_dnf(c, depth)
  lhs = c.lhs
  rhs = c.rhs
  
  if disj(lhs):
    if (disj(rhs) and d1 and d2) or (conj(rhs) and d1):
      # Both LHS and RHS are conjunctions.
      return (n1 + n2, d1 or d2)
    if (disj(rhs) and (d1 != d2)) or conj(rhs) or (atom(rhs) and d1):
      # Either LHS or RHS is a conjunction.
      return (1 + n1 + n2, d1 or d2)
    if disj(rhs) or atom(rhs):
      # Neither LHS nor RHS is a conjunction.
      return (2, False)
    assert False

  if conj(lhs):
    if (disj(rhs) and d2) or conj(rhs):
      # Both LHS and RHS are conjunctions.
      return (n1 + n2, d1 or d2)
    if disj(rhs) or atom(rhs):
      # Only LHS is a conjunction
      return (1 + n1 + n2, d1 or d2)
    assert False

  if atom(lhs):
    if (disj(rhs) and d2) or conj(rhs):
      # Only RHS is a disjunction
      return (1 + n1 + n2, d1 or d2)
    if disj(rhs) or atom(rhs):
      # Neither LHS nor RHS is a conjunction
      return (2, False)
    assert False

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
