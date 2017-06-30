

def find_leaves(x):
    return [i for i in x.keys() if len(x[i]) == 1]


def leaf_edge(x,j):
    if len(x[j]) != 1:
        raise RuntimeError("invalid state")
    k = list(x[j])[0]
    return j,k

# Flips a presumed tuple t.
def fliptup(t):
    return tuple(t[::-1])

# Prunes whatever leaf edges may exist in the named association map.
def prune_leaves_at(g,tag):
    x = g.assoc(tag)
    leaves = find_leaves(x)
    # print("map(%s) has %d leaves" % (tag,len(leaves)))
    # print("leaves(%s) = %s" % (tag,leaves))
    leaf_edges = [leaf_edge(x,j) for j in leaves]
    # print("leaf-edges(%s) = %s" % (tag,leaf_edges))
    count = 0
    for edge in leaf_edges:
        if tag == 'B':
            edge = fliptup(edge)
        g.remove(edge)
        count += 1
    return count

# Exhaustively prunes all "trails", i.e. edges t of g such that
# t is a leaf edge, or t eventually becomes a leaf edge as leaf edges 
# are iteratively pruned.
def prune_trails(g):
    hungry,step,count = True,0,0
    while hungry:
        pruned = {}
        pruned['A'] = prune_leaves_at(g,'A')
        pruned['B'] = prune_leaves_at(g,'B')
        print("step %d: pruned = %s" % (step,pruned))
        count += pruned['A'] + pruned['B']
        hungry = pruned['B'] > 0
        step += 1
    return count

