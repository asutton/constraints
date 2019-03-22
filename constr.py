
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

def approx1(c, depth = 0):
  print(f"{2 * depth * ' '}APPROX: {c}")

  if type(c) is Atom:
    print(f"{2 * depth * ' '}ATOM: {c} -> 0/0")
    return (0, 0)

  # Recursively count clauses in each subtree.
  p1 = approx1(c.lhs, depth + 1)
  p2 = approx1(c.rhs, depth + 2)
  
  # Get the number of nodes in each subtree.
  n1 = p1[0]
  n2 = p2[0]

  # Get the number of combinatoric distributions
  # in each subtree.
  d1 = p1[1]
  d2 = p2[1]

  if type(c) is Disj:
    # The additional number of subproblems depends on whether
    # this is a disjunction of CNF-like formulas or a disjunction
    # of disjunctions.

    # If both branches are disjunctions, then we're just
    # combining subproblems; this does not create more.
    if (type(c.lhs) is Disj) and (type(c.rhs) is Disj):
      return (n1 + n2, d1 + d2)

    # If only one branch is a disjunction, then this disjunction
    # adds one more clause.
    if (type(c.lhs) is Disj) != (type(c.rhs) is Disj):
      # If either branch resulted in a distribution, then this
      # will not contribute to the overall count.
      if d1 or d2:
        print(f"{2 * depth * ' '}LINEAR 1: {c} -> {1 + n1 + n2}/{d1 + d2}")
        return (n1 + n2, d1 + d2)

      # Otherwise, this will contribute 1 clause.
      print(f"{2 * depth * ' '}LINEAR 2: {c} -> {1 + n1 + n2}/{d1 + d2}")
      return (1 + n1 + n2, d1 + d2)

    # If either side was a conjunction there may have been a
    # distribution, so this contributes only one clause.
    if type(c.lhs) is Conj or type(c.rhs) is Conj:
      if d1 or d2:
        print(f"{2 * depth * ' '}PRIOR DIST: {c} -> {1 + n1 + n2}/{d1 + d2}")
        return (1 + n1 + n2, d1 + d2)

    # Otherwise, we have a disjunction of clauses in CNF (on
    # the surface), and this will contribute two subproblems.
    print(f"{2 * depth * ' '}NEW: {c} -> {2 + n1 + n2}/{d1 + d2}")
    return (2 + n1 + n2, d1 + d2)

  if type(c) is Conj:
    # The additional number of subproblems depends on whether
    # the conjunction is distributed over disjunctions.

    # This is a combinatoric distribution.
    if type(c.lhs) is Disj and type(c.rhs) is Disj:
      print(f"{2 * depth * ' '}FOIL: {c} -> {n1 * n2}/{1 + d1 + d2}")
      return (n1 * n2, 1 + d1 + d2)

    # If either side is a disjunction and there was a distribution,
    # then this will also produce a combinatoric distribution.
    if type(c.lhs) is Disj or type(c.rhs) is Disj:
      if d1 or d2:
        print(f"{2 * depth * ' '}REDIST 1: {c} -> {n1 * n2}/{1 + d1 + d2}")
        return (n1 * n2, 1 + d1 + d2)
      else:
        print(f"{2 * depth * ' '}REDIST 2: {c} -> {n1 * n2}/{1 + d1 + d2}")
        return (n1 + n2, 1 + d1 + d2)

    # Otherwise, this is not a distribution.
    print(f"{2 * depth * ' '}KEEP: {c} -> {n1 + n2}/{d1 + d2}")
    return (n1 + n2, d1 + d2)

  assert False

def approx(c):
  n, d = approx1(c)
  return n if n else 1 # Adjust 0's to 1s

def visit(c):
  if type(c) is Disj:
    return 1 + visit(c.lhs) + visit(c.rhs)
  else:
    return 0

def actual(c):
  return 1 + visit(c)
