import simplejson as json
from itertools import islice
from collections import defaultdict, deque, Counter

class Matcher(object):

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
        # return edges

    # Emits a forest of components, by (invasively) "peeling" each 
    # component from our tuple of association maps.  When there are
    # no more components to peel, the generator halts (and our
    # association maps will be empty).
    def forests(self):
        while len(self.a) or len(self.b):
            yield peel(self.a,self.b)




# Valence histogram for a given association map
def valhist(x):
    return dict(Counter(len(x[i]) for i in x))


#
# "Peels" a semi-random cluster from the adjacency maps x and y,
# starting at a "random-ish" node chosen from map x (which won't be 
# truly random; but rather will simply be the first key emited that 
# map's underlying dict struct).
#
# This it does by simply walking back and forth between the respective 
# association maps, and traversing the connected component identified 
# by our starting node.  As it does so, it invavisely plucks ("peels") 
# both nodes and edges of the component it traverses from the given 
# associaton maps.
#
# Note that while this operation is order-dependent, it can be applied 
# in either direction to the association maps on our Matcher struct.
#
def peel(x,y):
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

# Projects an edge sequence onto its two respective vertex sets. 
def vertexset(edgeseq):
    jj,kk = set(),set()
    for j,k in edgeseq:
        jj.add(j)
        kk.add(k)
    return jj,kk

# Given a sequence of edges, returns a tuple representing the size of 
# each respective vertex set.  
def classify(edgeseq):
    jj,kk = vertexset(edgeseq)
    return len(jj),len(kk) 

def partition_forest(g):
    p = defaultdict(list)
    for edgelist in g.forests():
        nj,nk = classify(edgelist)
        p[(nj,nk)].append(edgelist)
    return p

# Given a tuple of integers, returns a simple tag describing its
# multiplicity class.
def simplify(nj,nk):
    if (nj,nk) == (1,1): return '1-1'
    elif nj == 1: return '1-n'
    elif nk == 1: return 'm-1'
    else: return 'm-n'

def refine_partition(p):
    tags = ('1-1','1-n','m-1','m-n')
    r = defaultdict(dict)
    for nj,nk in sorted(p.keys()):
        tag = simplify(nj,nk)
        r[tag][(nj,nk)] = p[(nj,nk)] 
    for k in tags:
        if k not in r: 
            r[k] = {} 
    return r

def edgeseq2stats(edgeseq):
    return Matcher(edgeseq).stats()

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
            for edgelist in components: 
                stats = Matcher(edgelist).stats()
                count['edge'] += stats['edges']
                count['vertex-A'] += stats['vertices']['A']
                count['vertex-B'] += stats['vertices']['B']
        rows.append([longform[tag]] + [count[k] for k in headerkeys]) 
        for k in headerkeys: 
            total[k] += count[k] 
        total['class'] += len(compclasses)
    rows.append(["total"] + [total[k] for k in headerkeys]) 
    return rows,total

def innersum(sequence):
   return sum(len(x) for x in sequence)

#1234567890123456789012345678901234567890123456789012345678901234567890123456789
