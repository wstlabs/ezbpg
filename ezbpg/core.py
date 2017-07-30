import simplejson as json
from itertools import islice
from collections import OrderedDict, defaultdict, deque, Counter

class BipartiteGraph(object):
    """
    A simple representation of a BipartiteGraph.
    """

    def __init__(self,edgeseq):
        """
        :param edgeseq: An iterable container of edges
        :return: A bipartite graph
        """
        self.consume(edgeseq)

    def reset(self):
        self.seen = set()
        self.distinct = 0
        self.observed = 0
        self.a = defaultdict(set)
        self.b = defaultdict(set)

    @property
    def dims(self):
        return len(self.a),len(self.b)

    def __len__(self):
        return self.distinct

    def assoc(self,tag):
        if tag == 'A': return self.a
        if tag == 'B': return self.b
        raise ValueError("invalid map descriptor")

    def stats(self):
        return {
            'edges': self.distinct,
            'vertices': {
                'A':len(self.a),
                'B':len(self.b)
            }
        }

    # Returns a valence histogram for each association map. 
    def valhist(self):
        return {
            'A':valhist(self.a),
            'B':valhist(self.b)
        }

    # A pair of alternate accessors for our assocation maps a and b,
    # for serialization purposes.  Each returns a dict-of-list struct
    # (where the list of connecting vertices is also sorted) rather than 
    # the dict-of-set struct used to represent these maps internally.
    def aa(self):
        return {k:sorted(self.a[k]) for k in self.a}

    def bb(self):
        return {k:sorted(self.b[k]) for k in self.b}

    def add(self,edge):
        j,k = edge
        self.seen.add((j,k))
        self.a[j].add(k)
        self.b[k].add(j)
        self.observed += 1

    # Ingests an edge list for a bipartite graph  -- represented by a sequence
    # of tuples (j,k) of indices on the corresponding vertex sets A and B --
    # and projects these into two internal associatin maps (one for each
    # vertex set).
    def consume(self,edgeseq):
        self.reset()
        for edge in edgeseq:
            self.add(edge)
        self.distinct = len(self.seen)
        self.seen = None
        return self

    def contains(self,edge):
        j,k = edge
        return (
            j in self.a and k in self.a[j] and
            k in self.b and j in self.b[k]
        )

    # Like 'discard' but insists edge be present (raises otherwise). 
    def remove(self,edge):
        if self.contains(edge):
            j,k = edge
            self.a[j].remove(k)
            self.b[k].remove(j)
            if len(self.a[j]) == 0:
                del self.a[j]
            if len(self.b[k]) == 0:
                del self.b[k]
            self.distinct -= 1
        else:
            raise ValueError("can't remove edge %s - not present" % str(edge))

    # Similar in semantics to 'set.discard' -- removes and edge if present,
    # otherwise has no effect.
    def discard(self,edge):
        if self.contains(edge):
            self.remove(edge)

    def edges(self):
        edges = set()
        for j in self.a:
            for k in self.a[j]:
                yield (j,k)

    def isempty(self):
        return len(self.a) == 0 or len(self.b) == 0

    def peel(self):
        edges = peelfrom(self.a,self.b)
        return BipartiteGraph(edges) if edges else None

    # Emits a forest of components, by (invasively) "peeling" each 
    # component from our tuple of association maps.  When there are
    # no more components to peel, the generator halts (and our
    # association maps will be empty).
    def forest(self):
        while not self.isempty():
            yield self.peel()

    def partition(self):
        return Partition(self)


class Partition(object):
    """
    A simple container representing a special partition of BipartiteGraph structs
    represented as a dict-of-list structs, where the keys in the dicts are dimension
    tuples (e.g. (1,1), (1,3), (3,2), ...) and the values are lists of components
    having those dimensions.
    """

    def __init__(self,g):
        """
        Constructs a partition of the forest of connected components of the
        given graph :g, emptying :g in the process.
        """
        self.consume(g)

    def consume(self,g):
        self.r = partition_forest(g)

    def keys(self):
        yield from self.r.keys()

    def __iter__(self):
        yield from self.r.items()

    def __len__(self):
        return len(self.r)

    def refine(self):
        return RefinedPartition(self)


def partition_forest(g,sort=True):
    p = defaultdict(list)
    for subg in g.forest():
        p[subg.dims].append(subg)
    return p


class RefinedPartition(object):
    """
    A simple (immutable) container representing a 'refined partition' of a forest,
    wherein the keys are category groupings based on the tags ('1-1','1-n','m-1','m-n'),
    and their values are in turn the sub-partitions for each category.

    As with the Partition container, this is a volatile, wrapping container:
    the child lists will simply be raw member lists from the base partition
    (rather than cloned lists), for performance considerations.
    """

    def __init__(self,p):
        self.r = refined_partition(p)

    def __iter__(self):
        yield from self.r.items()

    def describe(self):
        return describe_partition(self.r)

    def walk(self):
        """Performs an ordered traversal of a refined partition :r, yielding a seguence
        of OrderedDict structs keyed on the fields ('cat','dims','seq','edges'), where each
        dict corresponds to a component in our forest.  [Need to explain these fields].
        """
        for k,category in self:
            for t in sorted(category.keys()):
                for i,edges in enumerate(category[t]):
                    items = [('cat',k),('dims',t),('seq',i+1),('edges',edges)]
                    yield OrderedDict(items)


def refined_partition(p):
    """
    Creates the underlying OrderedDict struct used by the RefinedPartition
    struct.  See the docstring for that class for details.
    """
    tags = ('1-1','1-n','m-1','m-n')
    r = OrderedDict((_,{}) for _ in tags)
    for k,v in p:
        tag = simplify(*k)
        r[tag][k] = v
    return r


# Valence histogram for a given association map
def valhist(x):
    return dict(Counter(len(x[i]) for i in x))

# multiplicity class.
def simplify(nj,nk):
    if (nj,nk) == (1,1): return '1-1'
    elif nj == 1: return '1-n'
    elif nk == 1: return 'm-1'
    else: return 'm-n'


#
# Given a refined partition struct r, generates a nice rowset describing
# counts of classes, components, edges and vertices per multiplicity
# category, along with a dict of their totals over all categories (which
# should align with the totals for edges and vertices from our initial
# bipartite graph).
#
longform = {
    '1-1':'1-to-1',    '1-n':'1-to-many',
    'm-1':'many-to-1', 'm-n':'many-to-many',
}
def describe_partition(r):
    total = defaultdict(int)
    headerkeys = ('class','component','edge','vertex-A','vertex-B')
    rows = [["classes","components","edges","vertices(A)","vertices(B)"]]
    for tag in sorted(r.keys()):
        count = defaultdict(int)
        compclasses = r[tag]
        count['class'] = len(compclasses)
        count['component'] = sum(len(r[tag][x]) for x in r[tag])
        for x in r[tag].keys():
            components = r[tag][x]
            for g in components:
                stats = g.stats()
                count['edge'] += stats['edges']
                count['vertex-A'] += stats['vertices']['A']
                count['vertex-B'] += stats['vertices']['B']
        rows.append([longform[tag]] + [count[k] for k in headerkeys])
        for k in headerkeys:
            total[k] += count[k]
        total['class'] += len(compclasses)
    rows.append(["total"] + [total[k] for k in headerkeys])
    return rows,total


def peelfrom(x,y):
    """
    A weird function which invasively "peels" a random connected component
    from the pair of adjacency maps :x and :y.  The "component" is provided
    in the form of a yielded sequence of edges (2-tuples of vertices from
    the original pair of adjency pays), each presented twice.

    As the iterator exhausts, it (invasively) pops from one or the other
    of the adjacency maps.  As such, this method is not "transaction-safe":
    if you stop the iteration before it's done, you'll almost certainly
    wind up with a pair of corrupted adjecency maps (and you won't have a
    meaningful edge list, either).  But if you let it run to the end, both
    the edge list and the adjacency maps will each be in a coherent state.

    As to why it presents each edge twice: that's a side effect of the
    algorithm's drop-dead simplicity.  Any approach which avoids this side
    effect would, necessarily, require -some- kind of overhead -- either
    some kind of internal memoization, or a more clever algorithm.

    Favoring siplicity, we elect to emit a "noisy" -- which is trivially
    de-duped, especailly if you feed the redundant edge sequence directly
    into the constructor for the BipartiteGraph class.  Which is in fact
    the itended use case for this function.
    """
    if not len(x) and len(y):
        return None
    edgelist = []
    jj = deque(islice(x.keys(),0,1))
    kk = deque()
    hungry = True
    while hungry:
        if len(jj):
            j = jj.popleft()
            if j in x:
                nodes = x.pop(j)
                for k in nodes:
                    yield j,k
                    kk.append(k)
        elif len(kk):
            k = kk.popleft()
            if k in y:
                nodes = y.pop(k)
                for j in nodes:
                    yield j,k
                    jj.append(j)
        else:
            hungry = False



# DEPRECATED
# An older version of the above, which produced a de-duped edgelist 
# (somewhat inefficiently), rather than yielding a sequence of (duped) edges. 
def __peel(x,y):
    if not len(x) and len(y):
        return None
    edgelist = []
    jj = deque(islice(x.keys(),0,1))
    kk = deque()
    hungry = True
    while hungry:
        if len(jj):
            j = jj.popleft()
            if j in x:
                nodes = x.pop(j)
                for k in nodes:
                    if (j,k) not in edgelist:
                        edgelist.append((j,k))
                    kk.append(k)
        elif len(kk):
            k = kk.popleft()
            if k in y:
                nodes = y.pop(k)
                for j in nodes:
                    if (j,k) not in edgelist:
                        edgelist.append((j,k))
                    jj.append(j)
        else:
            hungry = False
    return edgelist

def __partition_forest(g,sort=True):
    p = defaultdict(list)
    for subgraph in g.forest():
        if (sort):
            edgelist = sorted(edgelist)
        nj,nk = classify(edgelist)
        p[(nj,nk)].append(edgelist)
    return p

def __refine_partition(p):
    tags = ('1-1','1-n','m-1','m-n')
    r = OrderedDict((_,{}) for _ in tags)
    for nj,nk in sorted(p.keys()):
        tag = simplify(nj,nk)
        r[tag][(nj,nk)] = p[(nj,nk)]
    return r

# Projects an edge sequence onto its two respective vertex sets. 
def __vertexset(edgeseq):
    jj,kk = set(),set()
    for j,k in edgeseq:
        jj.add(j)
        kk.add(k)
    return jj,kk

# Given a sequence of edges, returns a tuple representing the size of 
# each respective vertex set.  
def __classify(edgeseq):
    jj,kk = __vertexset(edgeseq)
    return len(jj),len(kk)


