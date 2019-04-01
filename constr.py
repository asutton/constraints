
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

# Serialization

def dot(c, f):
  # Write the constraint expression c to output file f.
  f.write("digraph G {\n")
  n = Counter(0)
  c.dot(f, n)
  f.write("}")


# Predicates

def disj(c):
  return type(c) is Disj

def conj(c):
  return type(c) is Conj

def atom(c):
  return type(c) is Atom


# Additional facilities

from parse import parse
from dnf import dnf, approx_dnf, actual_dnf
from cnf import cnf, approx_cnf, actual_cnf

