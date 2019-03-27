
def recur(c, depth):
  # Recursively count clauses in each subtree.
  p1 = approx2(c.lhs, depth + 1)
  p2 = approx2(c.rhs, depth + 1)
  
  # Get the number of nodes in each subtree.
  n1 = p1[0]
  n2 = p2[0]

  # Get the number of distributions in each subtree.
  d1 = p1[1]
  d2 = p2[1]

  return n1, n2, d1, d2

def disj(c):
  return type(c) is Disj

def conj(c):
  return type(c) is Conj

def atom(c):
  return type(c) is Atom

def case_disj(c, depth):
  n1, n2, d1, d2 = recur(c, depth)
  lhs = c.lhs
  rhs = c.rhs

  if disj(lhs):
    if disj(rhs) or (conj(rhs) and d2):
      return (n1 + n2, d1 or d2)
    if conj(rhs) or atom(rhs):
      return (1 + n1 + n2, d1 or d2)
    assert False

    # if disj(rhs):
    #   return (n1 + n2, d1 or d2)
    # if conj(rhs) and d2:
    #   return (n1 + n2, d1 or d2)
    # if conj(rhs):
    #   return (1 + n1 + n2, d1 or d2)
    # if atom(rhs):
    #   return (1 + n1 + n2, d1 or d2)
    # assert False
  
  if conj(lhs):
    if (disj(rhs) and d1) or (conj(rhs) and d1 and d2):
      return (n1 + n2, True)
    if disj(rhs) or (conj(rhs) and (d1 != d2)) or (atom(rhs) and d1):
      return (1 + n1 + n2, d1 or d2)
    if conj(rhs) or atom(rhs):
      return (2, False)
    assert False

    # if disj(rhs) and d1:
    #   return (n1 + n2, True)
    # if disj(rhs):
    #   return (1 + n1 + n2, d1 or d2)
    # if conj(rhs) and d1 and d2:
    #   return (n1 + n2, True)
    # if conj(rhs) and (d1 != d2):
    #   return (1 + n1 + n2, True)
    # if conj(rhs):
    #   return (2, False)
    # if atom(rhs) and d1:
    #   return (1 + n1 + n2, d1 or d2)
    # if atom(rhs):
    #   return (2, False)
    # assert False

  if type(lhs) is Atom:
    if disj(rhs) or (conj(rhs) and d2):
      return (1 + n1 + n2, d1 or d2)
    if conj(rhs) or atom(rhs):
      return (2, False)
    assert False

    # if disj(rhs):
    #   return (1 + n1 + n2, d1 or d2)
    # if conj(rhs) and d2:
    #   return (1 + n1 + n2, d1 or d2)
    # if conj(rhs)
    #   return (2, False)
    # if atom(rhs):
    #   return (2, False)
    # assert False

def case_conj(c, depth):
  n1, n2, d1, d2 = recur(c, depth)
  lhs = c.lhs
  rhs = c.rhs
  
  if disj(lhs):
    if disj(rhs) or (conj(rhs) and d2):
      return (n1 * n2, True)
    if conj(rhs) or atom(rhs):
      return (n1 + n2, True)
    assert False

    # if disj(rhs):
    #   return (n1 * n2, True)
    # if conj(rhs) and d2:
    #   return (n1 * n2, True)
    # if conj(rhs):
    #   return (n1 + n2, True)
    # if atom(rhs):
    #   return (n1 + n2, True)
    # assert False
  
  elif conj(lhs):
    if (disj(rhs) and d1) or (conj(rhs) and d1 and d2):
      return (n1 * n2, True)
    if disj(rhs) or (conj(rhs) and (d1 != d2)) or (atom(rhs) and d1):
      return (n1 + n2, True)
    if conj(rhs) or atom(rhs):
      return (0, False)
    assert False

    # if disj(rhs) and d1:
    #   return (n1 * n2, True)
    # if disj(rhs):
    #   return (n1 + n2, True)
    # if conj(rhs) and d1 and d2:
    #   return (n1 * n2, True)
    # if conj(rhs) and d1 != d2:
    #   return (n1 + n2, True)
    # if conj(rhs):
    #   return (0, False)
    # if atom(rhs) and d1:
    #   return (n1 + n2, True)
    # if atom(rhs):
    #   return (0, False)
    # assert False

  elif atom(lhs):
    if disj(rhs) or (conj(rhs) and d2):
      return (n1 + n2, True)
    if conj(rhs) or atom(rhs):
      return (0, False)
    assert False

    # if disj(rhs):
    #   return (n1 + n2, True)
    # if conj(rhs) and d2:
    #   return (n1 + n2, True)
    # if conj(rhs):
    #   return (0, False)
    # if atom(rhs):
    #   return (0, False)

def case_atom(c, depth):
    print(f"{2 * depth * ' '}<<< X: {c} -> 0/0")
    return (0, False)  

def approx2(c, depth = 0):
  print(f"{2 * depth * ' '}>>> {c}")

  if type(c) is Atom: # x
    return case_atom(c, depth)

  if type(c) is Disj: # _ or _
    return case_disj(c, depth)

  if type(c) is Conj: # _ and _
    return case_conj(c, depth)

  assert False


