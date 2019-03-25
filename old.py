
# def approx1(c, depth = 0):
#   print(f"{2 * depth * ' '}APPROX: {c}")

#   if type(c) is Atom:
#     print(f"{2 * depth * ' '}ATOM: {c} -> 0/0")
#     return (0, 0)

#   # Recursively count clauses in each subtree.
#   p1 = approx1(c.lhs, depth + 1)
#   p2 = approx1(c.rhs, depth + 1)
  
#   # Get the number of nodes in each subtree.
#   n1 = p1[0]
#   n2 = p2[0]

#   # Get the number of combinatoric distributions
#   # in each subtree.
#   d1 = p1[1]
#   d2 = p2[1]

#   if type(c) is Disj:
#     # The additional number of subproblems depends on whether
#     # this is a disjunction of CNF-like formulas or a disjunction
#     # of disjunctions.

#     # If both branches are disjunctions, then we're just
#     # combining subproblems; this does not create more.
#     if (type(c.lhs) is Disj) and (type(c.rhs) is Disj):
#       print(f"{2 * depth * ' '}COMB DISJ: {c} -> {n1 + n2}/{d1 + d2}")
#       return (n1 + n2, d1 + d2)

#     # If only one branch is a disjunction, then this disjunction
#     # adds one more clause.
#     if (type(c.lhs) is Disj) != (type(c.rhs) is Disj):
#       # If either branch resulted in a distribution, then this
#       # will not contribute to the overall count.
#       if d1 or d2:
#         print(f"{2 * depth * ' '}LINEAR 1: {c} -> {1 + n1 + n2}/{d1 + d2}")
#         return (n1 + n2, d1 + d2)

#       # Otherwise, this will contribute 1 clause.
#       print(f"{2 * depth * ' '}LINEAR 2: {c} -> {1 + n1 + n2}/{d1 + d2}")
#       return (1 + n1 + n2, d1 + d2)

#     # If both sides are prior distributed conjunctions, then
#     # this is essentially a no-op
#     if type(c.lhs) is Conj and type(c.rhs) is Conj:
#       print(f"{2 * depth * ' '}COMB PRIOR CONJ: {c} -> {n1 + n2}/{d1 + d2}")
#       if d1 and d2:
#         return (n1 + n2, d1 + d2)

#     # If either side was a conjunction there may have been a
#     # distribution, so this contributes only one clause.
#     if type(c.lhs) is Conj or type(c.rhs) is Conj:
#       if d1 or d2:
#         print(f"{2 * depth * ' '}PRIOR DIST: {c} -> {1 + n1 + n2}/{d1 + d2}")
#         return (1 + n1 + n2, d1 + d2)

#     # Otherwise, we have a disjunction of clauses in CNF (on
#     # the surface), and this will contribute two subproblems.
#     print(f"{2 * depth * ' '}NEW: {c} -> {2 + n1 + n2}/{d1 + d2}")
#     return (2 + n1 + n2, d1 + d2)

#   if type(c) is Conj:
#     # The additional number of subproblems depends on whether
#     # the conjunction is distributed over disjunctions.

#     # This is a combinatoric distribution.
#     if type(c.lhs) is Disj and type(c.rhs) is Disj:
#       print(f"{2 * depth * ' '}FOIL: {c} -> {n1 * n2}/{1 + d1 + d2}")
#       return (n1 * n2, 1 + d1 + d2)

#     # If either side is a disjunction and there was a distribution,
#     # then this will also produce a combinatoric distribution.
#     if type(c.lhs) is Disj or type(c.rhs) is Disj:
#       if d1 or d2:
#         print(f"{2 * depth * ' '}REDIST 1: {c} -> {n1 * n2}/{1 + d1 + d2}")
#         return (n1 * n2, 1 + d1 + d2)
#       else:
#         print(f"{2 * depth * ' '}REDIST 2: {c} -> {n1 + n2}/{1 + d1 + d2}")
#         return (n1 + n2, 1 + d1 + d2)

#     # This is also potentially a combinatoric redist. Basically, both
#     # sides have been distributed through.
#     if type(c.lhs) is Conj and type(c.rhs) is Conj:
#       if d1 and d2:
#         print(f"{2 * depth * ' '}REDIST 3: {c} -> {n1 * n2}/{1 + d1 + d2}")
#         return (n1 * n2, 1 + d1 + d2)

#     # Otherwise, this is not a distribution.
#     print(f"{2 * depth * ' '}KEEP: {c} -> {n1 + n2}/{d1 + d2}")
#     return (n1 + n2, d1 + d2)

#   assert False
