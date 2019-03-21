
from collections import deque

class Constr:
  pass

class Conj(Constr):
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

  def __str__(self):
    return f"({self.lhs} and {self.rhs})"

  def __repr__(self):
    return f"Conj({repr(self.lhs)}, {repr(self.rhs)}))"

class Disj(Constr):
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

  def __str__(self):
    return f"({self.lhs} or {self.rhs})"

  def __repr__(self):
    return f"Disj({repr(self.lhs)}, {repr(self.rhs)}))"

class Atom(Constr):
  def __init__(self, id):
    self.id = id

  def __str__(self):
    return self.id

  def __repr__(self):
    return f"Atom({self.id})"

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
      print(f"{2 * depth * ' '}GOT FOIL: {r}")
      return r
    else:                 # (p or q) and a
      r = distl(lhs, rhs, depth)
      print(f"{2 * depth * ' '}GOT DISTL: {r}")
      return r
  elif type(rhs) is Disj: # a and (p or q)
    r = distr(lhs, rhs, depth)
    print(f"{2 * depth * ' '}GOT DISTR: {r}")
    return r      
  else:                   # a and p -- not distributed.
    r = Conj(lhs, rhs)
    print(f"{2 * depth * ' '}GOT CONJ: {r}")
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
  print(f"{2 * depth * ' '}DNF: {c}")

  # Already in DNF.
  if type(c) is Atom:
    print(f"{2 * depth * ' '}GOT ATOM: {c}")
    return c

  lhs = dnf(c.lhs, depth + 1)
  rhs = dnf(c.rhs, depth + 1)

  # Already in DNF (a or b)
  if type(c) is Disj:
    print(f"{2 * depth * ' '}GOT DNF: {c}")
    return Disj(lhs, rhs)

  # May not be in DNF -- may require distribution
  if type(c) is Conj:
    return dist(c, lhs, rhs, depth)

  assert False

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

def count(c, n, depth = 0):
  print(f"{2 * depth * ' '}COUNT: {c} -- {n}")
  print(f"{2 * depth * ' '}COUNT: {repr(c)}")

  if type(c) is Atom:
    print(f"{2 * depth * ' '}GOT DNF: 0")
    return 0

  lhs = c.lhs
  rhs = c.rhs

  if type(c) is Disj:
    n += 1
    count(lhs, n, depth + 1)
    count(rhs, n, depth + 1)
    print(f"{2 * depth * ' '}GOT DNF: {n}")
    return

  if type(c) is Conj:
    if type(lhs) is Disj:
      if type(rhs) is Disj: # (a or b) and (p or q)
        n *= 2
        count(lhs, n, depth + 1)
        n *= 2
        count(rhs, n, depth + 1)
        n += 1
        print(f"{2 * depth * ' '}GOT FOIL: {n}")
        return
      else:                 # (p or q) and a
        count(lhs, n, depth + 1)
        count(rhs, n, depth + 1)
        print(f"{2 * depth * ' '}GOT DISTL: {n}")
        return n
    elif type(rhs) is Disj: # a and (p or q)
      count(lhs, n, depth + 1)
      count(rhs, n, depth + 1)
      print(f"{2 * depth * ' '}GOT DISTR: {n}")
      return
    else:                   # a and p -- not distributed.
      print(f"{2 * depth * ' '}GOT CNF: {n}")
      return

def clauses(c):
  n = Counter(1)
  count(c, n)
  return n.value
