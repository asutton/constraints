
from collections import deque

class Counter:
  def __init__(self, n):
    self.value = n

  def __iadd__(self, n):
    self.value += n
    return self

  def __imul__(self, n):
    self.value *= n
    return self

  def __str__(self):
    return str(self.value)

class Constr:
  pass

class Conj(Constr):
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

  def opstr(self, e):
    # Add parens if the precedence of an operand is less than
    # the precedence of this expression.
    if type(e) is Disj:
      return f"({e})"
    else:
      return str(e)

  def __str__(self):
    # return f"{self.opstr(self.lhs)} and {self.opstr(self.rhs)}"
    return f"({self.lhs} and {self.rhs})"


  def __repr__(self):
    return f"Conj({repr(self.lhs)}, {repr(self.rhs)})"

  def dot(self, f, n):
    num = n.value
    n += 1
    this = f"and{num}"
    node = f"{this}[label=\"and\"];\n"
    f.write(node)
    lhs = self.lhs.dot(f, n)
    rhs = self.rhs.dot(f, n)
    larrow = f"{this} -> {lhs};\n"
    rarrow = f"{this} -> {rhs};\n"
    f.writelines([larrow, rarrow])
    return this


class Disj(Constr):
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

  def __str__(self):
    return f"({self.lhs} or {self.rhs})"

  def __repr__(self):
    return f"Disj({repr(self.lhs)}, {repr(self.rhs)})"

  def dot(self, f, n):
    num = n.value
    n += 1
    this = f"or{num}"
    node = f"{this}[label=\"or\"];\n"
    f.write(node)
    lhs = self.lhs.dot(f, n)
    rhs = self.rhs.dot(f, n)
    larrow = f"{this} -> {lhs};\n"
    rarrow = f"{this} -> {rhs};\n"
    f.writelines([larrow, rarrow])
    return this

class Atom(Constr):
  def __init__(self, id):
    self.id = id

  def __str__(self):
    return self.id

  def __repr__(self):
    return f"Atom({self.id})"

  def dot(self, f, n):
    num = n.value
    n += 1
    this = f"p{num}"
    node = f"{this}[label=\"{self.id}\"];\n"
    f.write(node)
    return this

def dot(c, f):
  f.write("digraph G {\n")
  n = Counter(0)
  c.dot(f, n)
  f.write("}")

class Token:
  eof = 0
  lparen = 1
  rparen = 2
  land = 3
  lor = 4
  ident = 5

  # Maps kinds to their spellings.
  names = {
    eof : "eof",
    lparen : "lparen",
    rparen : "rparen",
    land : "land",
    lor : "lor",
    ident : "ident"
  }

  def __init__(self, k, l):
    self.kind = k
    self.lexeme = l

  def __str__(self):
    if self.kind == Token.ident:
      return f"<{Token.names[self.kind]}:{self.lexeme}>"
    else:
      return f"<{Token.names[self.kind]}>"


def lex_string(s, f, l):
  toks = []
  while f != l:
    # Skip whitespace
    if s[f] in (' ', '\t', '\n'):
      f += 1
      continue
    
    # Match '('
    if s[f] == '(':
      toks += [Token(Token.lparen, s[f:f+1])]
      f += 1
      continue
    
    # Match ')'
    if s[f] == ')':
      toks += [Token(Token.rparen, s[f:f+1])]
      f += 1
      continue

    # Match identifiers and keywords
    if s[f].isalpha():
      n = f + 1
      while s[n].isalpha() or s[n].isdigit():
        n += 1
      w = s[f:n]
      if w == "and":
        toks += [Token(Token.land, w)]
      elif w == "or":
        toks += [Token(Token.lor, w)]
      else:
        toks += [Token(Token.ident, w)]
      f = n
      continue

    raise Exception(f"invalid character '{s[f]}'")

  return deque(toks)

def lex(s):
  return lex_string(s, 0, len(s))

class Parser:
  def __init__(self, toks):
    self.toks = toks
    self.eof = Token(Token.eof, None)

  def iseof(self):
    return len(self.toks) == 0

  def peek(self):
    if self.iseof():
      return self.eof
    else:
      return self.toks[0]

  def lookahead(self):
    return self.peek().kind

  def consume(self):
    assert not self.iseof();
    return self.toks.popleft()

  def match(self, k):
    if self.lookahead() == k:
      return self.consume()
    return self.eof

  def expect(self, k):
    if self.lookahead() == k:
      return self.consume()

    # FIXME: Improve diagnostics.
    raise Exception("syntax error")

  def parse_expr(self):
    return self.parse_or()

  def parse_or(self):
    e1 = self.parse_and()
    while self.lookahead() == Token.lor:
      self.consume()
      e2 = self.parse_and()
      e1 = Disj(e1, e2)
    return e1

  def parse_and(self):
    e1 = self.parse_atom()
    while self.lookahead() == Token.land:
      self.consume()
      e2 = self.parse_atom()
      e1 = Conj(e1, e2)
    return e1

  def parse_atom(self):
    if self.lookahead() == Token.ident:
      n = self.consume()
      return Atom(n.lexeme)

    if self.lookahead() == Token.lparen:
      self.consume()
      e = self.parse_expr()
      self.expect(Token.rparen)
      return e

def parse(s):
  p = Parser(lex(s))
  return p.parse_expr()

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

  # Already in DNF.
  if type(c) is Atom:
    # print(f"{2 * depth * ' '}GOT ATOM: {c}")
    return c

  lhs = dnf(c.lhs, depth + 1)
  rhs = dnf(c.rhs, depth + 1)

  # Already in DNF (a or b)
  if type(c) is Disj:
    # print(f"{2 * depth * ' '}GOT DNF: {c}")
    return Disj(lhs, rhs)

  # May not be in DNF -- may require distribution
  if type(c) is Conj:
    return dist(c, lhs, rhs, depth)

  assert False



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

## Disjunction cases

def case_disj_dd(c, depth):
  # (a or b) or (p or q)
  # Combines clauses.
  n1, n2, d1, d2 = recur(c, depth)
  n = n1 + n2
  d = d1 or d2
  print(f"{2 * depth * ' '}<<< D of DD: {c} -> {n}/{d}")
  return (n, d)

def case_disj_dc(c, depth):
  # (a or b) or (p and q)
  n1, n2, d1, d2 = recur(c, depth)
  if d2: # RHS was distributed; just combines
    n = n1 + n2
    d = d1 or d2
    print(f"{2 * depth * ' '}<<< D of D*: {c} -> {n}/{d}")
    return (n, d)
  else: # No distributions; additive increase.
    n = 1 + n1 + n2 # n2 is almost certainly 0
    assert n2 == 0
    d = d1 or d2
    print(f"{2 * depth * ' '}<<< D of DC: {c} -> {n}/{d}")
    return (n, d)

def case_disj_dx(c, depth):
  # (a or b) or x
  # Additive increase
  n1, n2, d1, d2 = recur(c, depth)
  n = 1 + n1 + n2
  assert n2 == 0
  d = d1 or d2
  assert d2 == False
  print(f"{2 * depth * ' '}<<< D of DX: {c} -> {n}/{d}")
  return (n, d)

def case_disj_cd(c, depth):
  # (a and b) or (p or q)
  n1, n2, d1, d2 = recur(c, depth)
  if d1: # LHS was distributed; combines clauses.
    n = n1 + n2
    d = d1 or d2
    print(f"{2 * depth * ' '}<<< D of *D: {c} -> {n}/{d}")
    return (n, d)
  else: # No distributions; additive increase.
    n = 1 + n1 + n2 # n1 is almost certainly 0
    assert n1 == 0
    d = d1 or d2
    print(f"{2 * depth * ' '}<<< D of CD: {c} -> {n}/{d}")
    return (n, d)

def case_disj_cc(c, depth):
  # (a and b) or (p and q)
  n1, n2, d1, d2 = recur(c, depth)
  if d1 and d2: # LHS and RHS were distributed; combines clauses.
    n = n1 + n2
    d = True
    print(f"{2 * depth * ' '}<<< D of **: {c} -> {n}/{d}")
    return (n, d)
  
  if d1 and not d2: # LHS was distributed; additive increase
    n = 1 + n1 + n2 # n2 is almost certainly 0
    assert n2 == 0
    d = d1
    print(f"{2 * depth * ' '}<<< D of *C: {c} -> {n}/{d}")
    return (n, d)

  if d2 and not d1: # RHS was distributed; additive increase
    n = 1 + n1 + n2 # n1 is almost certainly 0
    assert n1 == 0
    d = d2
    print(f"{2 * depth * ' '}<<< D of C*: {c} -> {n}/{d}")
    return (n, d)

  # No distributions
  if not d1 and not d2:          
    n = 2 + n1 + n2 # n1, n2 are almost certainly 0
    assert n1 == 0
    assert n2 == 0
    d = False
    print(f"{2 * depth * ' '}<<< D of CC: {c} -> {n}/{d}")
    return (n, d)

def case_disj_cx(c, depth):
  # (a and b) or x
  n1, n2, d1, d2 = recur(c, depth)
  assert n2 == 0 and not d2
  if d1: # LHS was distributed; additive increase
    n = 1 + n1
    d = True
    print(f"{2 * depth * ' '}<<< D of *X: {c} -> {n}/{d}")
    return (n, d)
  else:
    n = 2 + n1 # n1 is almost certainly 0
    assert n1 == 0
    d = False
    print(f"{2 * depth * ' '}<<< D of CX: {c} -> {n}/{d}")
    return (n, d)

def case_disj_xd(c, depth):
  # x or (p or q)
  # Additive increase
  n1, n2, d1, d2 = recur(c, depth)
  n = 1 + n2
  d = d2
  print(f"{2 * depth * ' '}<<< D of XD: {c} -> {n}/{d}")
  return (n, d)

def case_disj_xc(c, depth):
  # x or (p and q)
  n1, n2, d1, d2 = recur(c, depth)
  assert n1 == 0 and not d1
  if d2: # RHS was distributed; additive increase
    n = 1 + n2
    d = d2
    print(f"{2 * depth * ' '}<<< D of X*: {c} -> {n}/{d}")
    return (n, d)
  else:
    n = 2 + n2 # n2 is almost certainly 0
    d = False
    print(f"{2 * depth * ' '}<<< D of XC: {c} -> {n}/{d}")
    return (n, d)

def case_disj_xx(c, depth):
  # x or y
  # Creates two clauses.
  n1, n2, d1, d2 = recur(c, depth) # Can short-circuit
  print(f"{2 * depth * ' '}<<< D of XX: {c} -> {2}/{0}")
  return (2, 0)

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
    assert False
  
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

## Conjunction cases

def case_conj_dd(c, depth):
  # (a or b) and (p or q)
  # Applies foil.
  n1, n2, d1, d2 = recur(c, depth)
  n = n1 * n2
  d = True
  print(f"{2 * depth * ' '}<<< C of DD: {c} -> {n}/{d}")
  return (n, d)

def case_conj_dc(c, depth):
  # (a or b) and (p and q)
  n1, n2, d1, d2 = recur(c, depth)
  if d2: # RHS was previously distributed; applies foil.
    n = n1 * n2
    d = True
    print(f"{2 * depth * ' '}<<< C of D*: {c} -> {n}/{d}")
    return (n, d)
  else: # Not distributed; just distributes;
    n = n1 + n2 # n2 is almost certainly 0
    assert n2 == 0
    d = True
    print(f"{2 * depth * ' '}<<< C of DC: {c} -> {n}/{d}")
    return (n, d)

def case_conj_dx(c, depth):
  # (a or b) and x
  # Just distributes x across.
  n1, n2, d1, d2 = recur(c, depth)
  n = n1
  d = True
  print(f"{2 * depth * ' '}<<< C of DX: {c} -> {n}/{d}")
  return (n, d)

def case_conj_cd(c, depth):
  # (a and b) or (p or q)
  n1, n2, d1, d2 = recur(c, depth)
  if d1: # LHS was previously distributed; applies foil.
    n = n1 * n2
    d = True
    print(f"{2 * depth * ' '}<<< C of D*: {c} -> {n}/{d}")
    return (n, d)
  else: # Not distributed; just distributes
    n = n1 + n2 # n1 is almost certainly 0
    assert n1 == 0
    d = True
    print(f"{2 * depth * ' '}<<< C of DC: {c} -> {n}/{d}")
    return (n, d)

def case_conj_cc(c, depth):
  # (a and b) and (p and q)
  n1, n2, d1, d2 = recur(c, depth)
  if d1 and d2: # LHS and RHS were distributed; applies foil
    n = n1 * n2
    d = True
    print(f"{2 * depth * ' '}<<< C of **: {c} -> {n}/{d}")
    return (n, d)
  
  # FIXME: The 2nd and 3rd cases can be combined.
  if d1 and not d2: # LHS was distributed; just distributes.
    n = n1 + n2 # n2 is almost certainly 0
    assert n2 == 0
    d = True
    print(f"{2 * depth * ' '}<<< C of *C: {c} -> {n}/{d}")
    return (n, d)

  if d2 and not d1: # RHS was distributed; just distributes.
    n = n1 + n2 # n1 is almost certainly 0
    assert n1 == 0
    d = True
    print(f"{2 * depth * ' '}<<< C of C*: {c} -> {n}/{d}")
    return (n, d)

  if not d1 and not d2: # Neither distributed
    n = n1 + n2 # n is almost certainly 0.
    assert n1 == 0
    assert n2 == 0
    d = False
    print(f"{2 * depth * ' '}<<< C of CC: {c} -> {n}/{d}")
    return (n, d)

def case_conj_cx(c, depth):
  # (a and b) and x
  n1, n2, d1, d2 = recur(c, depth)
  if d1: # LHS was distributed; just distributes x across.
    n = n1
    d = True
    print(f"{2 * depth * ' '}<<< C of *X: {c} -> {n}/{d}")
    return (n, d)
  else:
    n = n1 # n1 is almost certainly 0
    assert n1 == 0
    d = False
    print(f"{2 * depth * ' '}<<< C of CX: {c} -> {n}/{d}")
    return (n, d)

def case_conj_xd(c, depth):
  # x and (p or q)
  # Just distributes x across.
  n1, n2, d1, d2 = recur(c, depth)
  n = n2
  d = True
  print(f"{2 * depth * ' '}<<< C of XD: {c} -> {n}/{d}")
  return (n, d)

def case_conj_xc(c, depth):
  # x or (p and q)
  n1, n2, d1, d2 = recur(c, depth)
  if d2: # RHS was distributed; just distributes x across.
    n = n2
    d = True
    print(f"{2 * depth * ' '}<<< C of X*: {c} -> {n}/{d}")
    return (n, d)
  else: # RHS not distributed;
    n = n2 # Almost certainly 0.
    assert n2 == 0
    d = False
    print(f"{2 * depth * ' '}<<< C of XC: {c} -> {n}/{d}")
    return (n, d)

def case_conj_xx(c, depth):
  # x or y
  # Contributes no clauses and does not distribute.
  n1, n2, d1, d2 = recur(c, depth) # Can short-circuit.
  print(f"{2 * depth * ' '}<<< C of XX: {c} -> {0}/{0}")
  return (0, False)


def case_conj(c, depth):
  # print(f"{2 * depth * ' '}>>> D of ??: {c}")
  if type(c.lhs) is Disj: # (a or b) and _
    if type(c.rhs) is Disj: # (a or b) and (p or q)
      return case_conj_dd(c, depth)
    elif type(c.rhs) is Conj: # (a or b) and (p and q)
      return case_conj_dc(c, depth)
    elif type(c.rhs) is Atom: # (a or b) and p
      return case_conj_dx(c, depth)
  
  elif type(c.lhs) is Conj: # (a and b) and _
    if type(c.rhs) is Disj: # (a and b) and (p or q)
      return case_conj_cd(c, depth)
    if type(c.rhs) is Conj: # (a and b) and (p and q)
      return case_conj_cc(c, depth)
    if type(c.rhs) is Atom: # (a and b) and x
      return case_conj_cx(c, depth)

  elif type(c.lhs) is Atom: # x and _
    if type(c.rhs) is Disj: # x and (p or q)
      return case_conj_xd(c, depth)
    if type(c.rhs) is Conj: # x and (p and q)
      return case_conj_xc(c, depth)
    if type(c.rhs) is Atom: # x and y
      return case_conj_xx(c, depth)

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


def approx(c):
  n, d = approx2(c)
  return n if n else 1 # Adjust 0's to 1s

def visit(c):
  if type(c) is Disj:
    return 1 + visit(c.lhs) + visit(c.rhs)
  else:
    return 0

def actual(c):
  return 1 + visit(c)
