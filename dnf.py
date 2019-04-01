from constr import *

def dist(c, lhs, rhs, depth):
  if type(lhs) is Disj:
    if type(rhs) is Disj: # (a or b) and (p or q)
      r = foil(lhs, rhs, depth)
      # print(f"{2 * depth * ' '}GOT FOIL: {r}")
      return r
    else:                 # (p or q) and a
      r = distl(lhs, rhs, depth)
      # print(f"{2 * depth * ' '}GOT DISTL: {r}")
      return r
  elif type(rhs) is Disj: # a and (p or q)
    r = distr(lhs, rhs, depth)
    # print(f"{2 * depth * ' '}GOT DISTR: {r}")
    return r      
  else:                   # a and p -- not distributed.
    r = Conj(lhs, rhs)
    # print(f"{2 * depth * ' '}GOT CONJ: {r}")
    return r

  assert False

def distr(lhs, rhs, depth):
  # have a and (p or q)
  c1 = Conj(lhs, rhs.lhs)
  c1 = dist(c1, c1.lhs, c1.rhs, depth + 1)
  
  c2 = Conj(lhs, rhs.rhs)
  c2 = dist(c2, c2.lhs, c2.rhs, depth + 1)

  return Disj(c1, c2)

def distl(lhs, rhs, depth):
  # have (p or q) and a
  c1 = Conj(lhs.lhs, rhs)
  c1 = dist(c1, c1.lhs, c1.rhs, depth + 1)

  c2 = Conj(lhs.rhs, rhs)
  c2 = dist(c2, c2.lhs, c2.rhs, depth + 1)

  return Disj(c1, c2)

def foil(lhs, rhs, depth):
  # have (a or b) and (c or d)
  f = Conj(lhs.lhs, rhs.lhs)
  f = dist(f, f.lhs, f.rhs, depth + 1)

  o = Conj(lhs.lhs, rhs.rhs)
  o = dist(o, o.lhs, o.rhs, depth + 1)

  i = Conj(lhs.rhs, rhs.lhs)
  i = dist(i, i.lhs, i.rhs, depth + 1)

  l = Conj(lhs.rhs, rhs.rhs)
  l = dist(l, l.lhs, l.rhs, depth + 1)
  
  return Disj(Disj(Disj(f, o), i), l)

def dnf(c, depth = 0):
  # print(f"{2 * depth * ' '}DNF: {c}")

  if type(c) is Atom:
    # Matches p -- can't distribute
    # print(f"{2 * depth * ' '}GOT ATOM: {c}")
    return c

  lhs = dnf(c.lhs, depth + 1)
  rhs = dnf(c.rhs, depth + 1)

  if type(c) is Disj:
    # Matches p or q -- no transformation needed.
    # print(f"{2 * depth * ' '}GOT DNF: {c}")
    return Disj(lhs, rhs)

  if type(c) is Conj:
    # Matches p and q -- need to distribute
    # print(f"{2 * depth * ' '}GOT DNF: {c}")
    return dist(c, lhs, rhs, depth)

  assert False

# Counting

def recur_dnf(c, depth):
  # Recursively count clauses in each subtree.
  p1 = approx_dnf_recur(c.lhs, depth + 1)
  p2 = approx_dnf_recur(c.rhs, depth + 1)
  
  # Get the number of nodes in each subtree.
  n1 = p1[0]
  n2 = p2[0]

  # Get the number of distributions in each subtree.
  d1 = p1[1]
  d2 = p2[1]

  return n1, n2, d1, d2

def approx_dnf_disj(c, depth):
  n1, n2, d1, d2 = recur_dnf(c, depth)
  lhs = c.lhs
  rhs = c.rhs

  if disj(lhs):
    if disj(rhs) or (conj(rhs) and d2):
      return (n1 + n2, d1 or d2)
    if conj(rhs) or atom(rhs):
      return (1 + n1 + n2, d1 or d2)
    assert False

  if conj(lhs):
    if (disj(rhs) and d1) or (conj(rhs) and d1 and d2):
      return (n1 + n2, True)
    if disj(rhs) or (conj(rhs) and (d1 != d2)) or (atom(rhs) and d1):
      return (1 + n1 + n2, d1 or d2)
    if conj(rhs) or atom(rhs):
      return (2, False)
    assert False

  if atom(lhs):
    if disj(rhs) or (conj(rhs) and d2):
      return (1 + n1 + n2, d1 or d2)
    if conj(rhs) or atom(rhs):
      return (2, False)
    assert False

def approx_dnf_conj(c, depth):
  # Matches _ and _; distributes when either LHS or RHS is
  # a disjunction.
  n1, n2, d1, d2 = recur_dnf(c, depth)
  lhs = c.lhs
  rhs = c.rhs
  
  if disj(lhs):
    if disj(rhs) or (conj(rhs) and d2):
      return (n1 * n2, True)
    if conj(rhs) or atom(rhs):
      return (n1 + n2, True)
    assert False

  elif conj(lhs):
    if (disj(rhs) and d1) or (conj(rhs) and d1 and d2):
      return (n1 * n2, True)
    if disj(rhs) or (conj(rhs) and (d1 != d2)) or (atom(rhs) and d1):
      return (n1 + n2, True)
    if conj(rhs) or atom(rhs):
      return (0, False)
    assert False

  elif atom(lhs):
    if disj(rhs) or (conj(rhs) and d2):
      return (n1 + n2, True)
    if conj(rhs) or atom(rhs):
      return (0, False)
    assert False

def approx_dnf_atom(c, depth):
    print(f"{2 * depth * ' '}<<< X: {c} -> 0/0")
    return (0, False)  

def approx_dnf_recur(c, depth = 0):
  print(f"{2 * depth * ' '}>>> {c}")

  if atom(c): # x
    return approx_dnf_atom(c, depth)

  if disj(c): # _ or _
    return approx_dnf_disj(c, depth)

  if conj(c): # _ and _
    return approx_dnf_conj(c, depth)

  assert False


def approx_dnf(c):
  # FIXME: This isn't actually an approximation.
  n, d = approx_dnf_recur(c)
  return n if n else 1 # Adjust 0's to 1s


def actual_dnf_recur(c):
  if type(c) is Disj:
    return 1 + actual_dnf_recur(c.lhs) + actual_dnf_recur(c.rhs)
  else:
    return 0

def actual_dnf(c):
  # FIXME: This is not well named.
  return 1 + actual_dnf_recur(c)
