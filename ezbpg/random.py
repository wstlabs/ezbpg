from random import randint

# Generates a sequence of r tuples (j,k) where j and k are chosen from
# uniform distribtions over the intervals [0,m) and [0,n) respectively.
#
# Which in turn are intended to represent indices from the vertex sets 
# A and B which form the backbone of our bipartite graph.
#

def randtup(m,n):
    j = randint(0,m)
    k = randint(0,n)
    return j,k

def generate(m,n,limit=None,exact=None):
    assert m > 0, "first sample size must be greater than zero"
    assert n > 0, "second sample size must be greater than zero"
    assert limit is not None or exact is not None, "need a 'limit' or an 'exact' parameter"
    assert limit is None or exact is None, "'limit' and 'exact' parameters are mutually exclusive"
    if limit is not None:
        for _ in range(0,limit):
            yield randtup(m,n)
    elif exact is not None:
        seen = set()
        for _ in range(0,exact):
            t = randtup(m,n)
            if t not in seen:
                seen.add(t)
                yield t 
    else:
        raise RuntimeError("invalid state")


