import os, sys
from collections import Counter
from tabulate import tabulate
from itertools import combinations
import ioany
from . import ioutil

"""
A nifty module of nifty support functions.
"""

def mkdir_soft(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

def process(g):
    """Partitions and refines our graph :g, and prints some nice stats about it."""
    r = g.partition().refine()
    rows,total = r.describe()
    print(tabulate(rows,headers="firstrow"))
    print("Making for %d components total." % total['component'])
    return r

def project(outdir,r):
    rowset,cluster = r.project()
    print("rowset = %d, cluster = %d" % (len(rowset),len(cluster)))

    fields = ('a','b','cluster')
    outpath = "%s/rowset.csv" % outdir
    ioany.save_csv(outpath,rowset,header=fields)

    fields = ('cluster','na','nb','depth')
    outpath = "%s/cluster.csv" % outdir
    ioany.save_csv(outpath,cluster,header=fields)

def dumpall(outdir,r):
    mkdir_soft(outdir)
    for tag,category in r.walk2():
        print("extracting category '%s' .." % tag)
        subdir = "%s/%s" % (outdir,tag);
        mkdir_soft(subdir)
        for r in category:
            nj,nk = r['dims']
            i,g = r['seq'],r['graph']
            basefile = "%d,%d-%d.csv" % (nj,nk,i)
            outpath = "%s/%s" % (subdir,basefile)
            edgelist = sorted(g.edges())
            with open(outpath,"wt") as f:
                ioutil.save_edges(f,edgelist)

def flatten(d):
    """
    Clobbers the 'graph' element of our dict with its stringified version,
    to make the dict itself printable.
    """
    g = d['graph']
    d['graph'] = str(g)
    return d

def stroll_over(r):
    for tag,category in r.walk2():
        print("tag = %s .." % tag)
        for r in category:
            d = flatten(r)
            print(r)

def stroll(r):
    for d in r.walk():
        yield flatten(d)

def neighbors_a(g):
    for bnode,alist in g.b.items():
        # print(f'bnode={bnode},alist={alist}')
        for pair in combinations(alist,2):
            yield pair

def neighbor_graph_a(g):
    pairs = neighbors_a(g)
    return Counter(pairs)

def __neighbor_graph_a(g):
    w = defaultdict(int)
    for bnode,alist in g.b.items():
        print(f'bnode={bnode},alist={alist}')
        for pair in combinations(alist,2):
            w[pair] += 1
    return w

