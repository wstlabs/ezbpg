"""
Provides a simple container class for simple bipartite graphs with facilities summary statistics. 
"""
import os
import io
import csv
import itertools
from collections import defaultdict, deque, Counter
from tabulate import tabulate
from dataclasses import dataclass
from typing import Tuple, List, Dict, DefaultDict, Iterator, Deque, Any, Optional

Vertex = str 
AdjMap = DefaultDict[Vertex, set] 
AdjMapSorted = Dict[Vertex, List[Vertex]] 
EdgePair = Tuple[Vertex, Vertex]
RowIter = Iterator[List[str]]
MultPair = Tuple[int, int]
ForestMap = DefaultDict[Tuple[int, int], List['BipartiteGraph']]

@dataclass
class BPGTally(object):
    """A simple counting struct providing number of distinct and observed edges, respectively, 
    after consuming a sequence of (possibly duplicate) edges."""
    distinct: int 
    observed: int 

    @property
    def redundant(self) -> int:
        return self.observed - self.distinct

    @property
    def caption(self) -> str:
        pl: str = '' if self.distinct == 1 else 's'
        return f"{self.distinct} distinct edge{pl} (out of {self.observed} observed, with {self.redundant} redundant)"


class BipartiteGraph:
    """
    A simple representation of a BipartiteGraph.
    """

    def __init__(self, edgeseq: Optional[Iterator[EdgePair]]) -> None:
        """
        Args:
            edgeseq (optional): an iterator of edge pairs
        """
        self.reset()
        if edgeseq is None:
            edgeseq = (_ for _ in [])
        self.consume(edgeseq)

    def reset(self) -> None:
        """
        Resets the container to its default (empty) state. 
        """
        self.a: AdjMap = defaultdict(set) 
        self.b: AdjMap = defaultdict(set) 
        self.tally = BPGTally(0, 0)

    def consume(self, edgeseq: Iterator[EdgePair]) -> None:
        """Ingests a sequence of edges (adding each edge pair if not already seen"""
        self.reset()
        for edge in edgeseq:
            self.add(edge)

    def has_edge(self, edge: EdgePair) -> bool:
        """Returns True if the given :edge tuple exists in our graph, False otherwise"""
        (j, k) = edge
        return (j in self.a) and (k in self.b) and (k in self.a[j]) and (j in self.b[k])

    def add(self, edge: EdgePair):
        """Adds an :edge tuple (a tuple representing a pair vertices) to the graph, if it doesn't already exist."""
        if not self.has_edge(edge):
            (j, k) = edge
            self.a[j].add(k)
            self.b[k].add(j)
            self.tally.distinct += 1
        self.tally.observed += 1

    @property
    def dims(self) -> Tuple[int, int]:
        return (len(self.a), len(self.b))

    def __len__(self) -> int:
        return self.tally.distinct

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name}(edges={len(self)},A={len(self.a)},B={len(self.b)})"

    def stats(self) -> Dict[str, Any]:
        return {
            'edges': self.tally.distinct,
            'vertices': {
                'A': len(self.a),
                'B': len(self.b)
            }
        }

    # Returns a dict of valence histograms for each adjacency map. 
    def valence_histogram(self) -> Dict[str, Any]:
        return {'A': _valhist(self.a), 'B': _valhist(self.b)}

    # A pair of alternate accessors for our assocation maps a and b,
    # for serialization purposes.  Each returns a dict-of-list struct
    # (where the list of connecting vertices is also sorted) rather than 
    # the dict-of-set struct used to represent these maps internally.
    def aa(self) -> AdjMapSorted:
        return {k: sorted(self.a[k]) for k in self.a}

    def bb(self) -> AdjMapSorted:
        return {k: sorted(self.b[k]) for k in self.b}

    def remove(self, edge: EdgePair, strict: bool = True) -> None:
        """Removes an :edge from our graph, which it is presumed to contain."""
        if self.has_edge(edge):
            (j, k) = edge
            self.a[j].remove(k)
            self.b[k].remove(j)
            if len(self.a[j]) == 0:
                del self.a[j]
            if len(self.b[k]) == 0:
                del self.b[k]
            self.tally.distinct -= 1
        elif strict:
            raise ValueError("can't remove edge %s - not present" % str(edge))

    def edges(self, sort: bool = False) -> Iterator[EdgePair]:
        for j in self.a:
            if sort:
                for k in sorted(self.a[j]):
                    yield (j, k)
            else:
                for k in self.a[j]:
                    yield (j, k)

    def is_empty(self) -> bool:
        """Returns True if the graph is empty, false otherwise"""
        return len(self.a) == 0 and len(self.b) == 0

    def peel(self) -> 'BipartiteGraph':
        """Assuming our graph is non-empty, invasively 'peels' a component structure as defined in the 
        `peel_component` function in this module.  If called on a empty graph, an exception is raised."""
        edges = peel_component(self.a, self.b)
        return BipartiteGraph(edges)

    def extract_components(self):
        """Extracts a sequence of components, by (invasively) "peeling" each component from 
        our tuple of association maps.  When there are no more components to peel, the generator 
        halts (and our association maps will be empty).
        """
        while not self.is_empty():
            yield self.peel()
        self.reset()

    def partition(self) -> 'BipartiteGraphPartition':
        return BipartiteGraphPartition(self)

    def write_csv(self, f: io.TextIOWrapper, csvargs: Optional[Dict[str, Any]] = None) -> None: 
        if csvargs is None:
            csvargs = {}
        writer = csv.writer(f, **csvargs)
        for edge in self.edges():
            writer.writerow(edge)

    def save_csv(self, path: str, encoding: str = 'utf-8', csvargs: Optional[Dict[str, Any]] = None) -> None:
        with open(path, "wt", encoding=encoding) as f:
            return self.write_csv(f, csvargs)

    @classmethod
    def read_csv(cls, path: str, encoding: str = 'utf-8', csvargs: Optional[Dict[str, Any]] = None) -> 'BipartiteGraph': 
        rowiter = _csviter(path, encoding, csvargs)
        edgeseq = (_row2edge(row) for row in rowiter)
        return BipartiteGraph(edgeseq)


class BipartiteGraphPartition(object):
    """
    A simple container representing a special partition of BipartiteGraph structs
    represented as a dict-of-list structs, where the keys in the dicts are tuples 
    indicating cardinality (e.g. (1,1), (1,3), (3,2), ...) and the values are lists 
    of components having those dimensions.
    """

    def __init__(self, g: BipartiteGraph) -> None:
        """
        Constructs a partition of the forest of connected components of the
        given graph :g, emptying :g in the process.
        """
        self.consume(g)

    def consume(self, g) -> None:
        self.r: ForestMap = partition_forest(g)

    def keys(self) -> Iterator[MultPair]:
        yield from self.r.keys()

    def items(self) -> Iterator[Tuple[MultPair, List['BipartiteGraph']]]:
        yield from self.r.items()

    def __len__(self) -> int:
        return len(self.r)

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name}(len={len(self)})"

    def refine(self) -> 'RefinedPartition':
        return RefinedPartition(self)


def partition_forest(g: BipartiteGraph, sort: bool = True) -> ForestMap: 
    p: ForestMap = defaultdict(list)
    for subg in g.extract_components():
        p[subg.dims].append(subg)
    return p


@dataclass
class RPInfo(object):
    category: str
    dims: Tuple[int, int]
    seq: int
    graph: BipartiteGraph

    @property
    def caption(self) -> str:
        _dims = str(self.dims).replace(' ', '')
        return f"{self.category}: dims={_dims}, seq={self.seq} : {self.graph}"

@dataclass
class RPSurvey(object):
    rows: Tuple[List[List[str]]]
    total: Dict[str, int]

    def describe(self) -> str: 
        return tabulate(self.rows, headers='firstrow')

class RefinedPartition(object):
    """
    A simple (immutable) container representing a 'refined partition' of a forest,
    wherein the keys are category groupings based on the tags ('1-1','1-n','m-1','m-n'),
    and their values are in turn the sub-partitions for each category.

    As with the Partition container, this is a volatile, wrapping container:
    the child lists will simply be raw member lists from the base partition
    (rather than cloned lists), for performance considerations.
    """

    def __init__(self, p: BipartiteGraphPartition) -> None:
        self.r: Dict[str, dict] = build_refined_partition(p)
        self.survey: RPSurvey = survey_refined_partition(self.r)

    def items(self) -> Iterator[Tuple[str, dict]]:
        yield from self.r.items()

    def walk(self) -> Iterator[RPInfo]:
        """Performs an ordered traversal, yielding a sequence of RPInfo structs for each
        component in our forest."""
        for (k, category) in self.items():
            for t in sorted(category.keys()):
                for (i, graph) in enumerate(category[t]):
                    param = {'category': k, 'dims': t, 'seq': i + 1, 'graph': graph}
                    yield RPInfo(**param)

    def project(self) -> Tuple[list, list]:
        return project_refined_partition(self)

    def extract_categories(self, outdir: str) -> None:
        mkdir_soft(outdir)
        for (key, group) in itertools.groupby(self.walk(), lambda x: x.category): 
            print(f"extracting category '{key}' ..")
            subdir = f"{outdir}/{key}"
            mkdir_soft(subdir)
            for info in group: 
                (nj, nk) = info.dims
                outpath = f"{subdir}/{nj},{nk}-{info.seq}.csv"
                info.graph.save_csv(outpath)

#
# Various support functions.  
# None of these are likely to be useful outside this module.
#

def build_refined_partition(p: BipartiteGraphPartition) -> Dict[str, dict]: 
    """Creates the underlying dict used by the RefinedPartition struct.  
    See the docstring for that class for details."""
    tags = ('1-1', '1-n', 'm-1', 'm-n')
    r: Dict[str, dict] = {tag: {} for tag in tags}
    for (multpair, graphlist) in p.items():
        tag = simplify_multpair(multpair)
        r[tag][multpair] = graphlist 
    return r

def project_refined_partition(r: RefinedPartition) -> Tuple[list, list]:
    """(DEPRECATED) Given a RefinedPartition object,
    returns a pair of dataframe-like structs showing how each edge maps to a specific
    component.  Useful for detailed investigations, but currently deprecated."""
    rowset = []
    cluster, j = [], 1
    for (key, group) in itertools.groupby(r.walk(), lambda x: x.category): 
        for info in group:
            depth = 0
            (na, nb) = info.dims
            (_, g) = (info.seq, info.graph)
            for (a, b) in g.edges():
                rowset.append([a, b, j])
                depth += 1
            cluster.append([j, na, nb, depth])
            j += 1
    return (rowset, cluster)


def _valhist(x: AdjMap) -> Dict[int, int]:
    """Returns the valence histogram for a given adjacency map"""
    return dict(Counter(len(x[k]) for k in x))

def simplify_multpair(multpair: MultPair):
    """Given a MultPair (a pair of integers representing a multiplicity class, returns a 
    string descriptor for its idealized equivalence class."""
    (nj, nk) = multpair
    if (nj, nk) == (1, 1): return '1-1'
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
    '1-1': '1-to-1',    '1-n': '1-to-many',
    'm-1': 'many-to-1', 'm-n': 'many-to-many',
}
def survey_refined_partition(r: Dict[str, dict]) -> RPSurvey: 
    """Given the internal dict for a RefinedPartition object, returns a pair of 
    special survey structures used for the nifty `describe` method for that class."""
    total: DefaultDict[str, int] = defaultdict(int)
    headerkeys = ('class', 'component', 'edge', 'vertex-A', 'vertex-B')
    rows = [['classes', 'components', 'edges', 'vertices(A)', 'vertices(B)']]
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
        rows.append([longform[tag]] + [str(count[k]) for k in headerkeys])
        for k in headerkeys:
            total[k] += count[k]
    rows.append(["total"] + [str(total[k]) for k in headerkeys])
    return RPSurvey(rows, dict(total))


def peel_component(x: AdjMap, y: AdjMap) -> Iterator[EdgePair]:
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
    if bool(x) != bool(y):
        raise RuntimeError("corrupted state")
    if not (x and y):
        raise RuntimeError("invalid usage - empty adjacency map pair")
    jj: Deque = deque(itertools.islice(x.keys(), 0, 1))
    kk: Deque = deque()
    hungry = True
    while hungry:
        if len(jj):
            j = jj.popleft()
            if j in x:
                nodes = x.pop(j)
                for k in nodes:
                    yield (j, k)
                    kk.append(k)
        elif len(kk):
            k = kk.popleft()
            if k in y:
                nodes = y.pop(k)
                for j in nodes:
                    yield (j, k)
                    jj.append(j)
        else:
            hungry = False


def _csviter(path: str, encoding: str = 'utf-8', csvargs: Optional[Dict[str, Any]] = None) -> RowIter: 
    """A convenience function to produce a csv row iterator from the given arguments in the natural way."""
    if csvargs is None:
        csvargs = {}
    with open(path, "rt", encoding=encoding) as f:
        yield from csv.reader(f, **csvargs)

def _row2edge(row: List[str]) -> EdgePair: 
    """
    Takes a parsed CSV row (assumed to be of length 2), and returns a proper edge pair.
    This is of course a trivial mapping, equivalent to tuple(row). Tt only exists to verify the row length constraint.
    """ 
    if len(row) != 2:
        raise ValueError("invalid row")
    return tuple(row)

def mkdir_soft(dirpath: str) -> None:
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

