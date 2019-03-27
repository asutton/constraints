from collections import deque
from constr import *

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
