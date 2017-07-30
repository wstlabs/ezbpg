import copy
import os, sys, argparse
import simplejson as json
from collections import OrderedDict
from tabulate import tabulate
import ezbpg
from ezbpg.core import partition_forest, refine_partition, describe_partition

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", help="csv file to parse", required=True)
    parser.add_argument("--stroll", help="stroll", action="store_true")
    parser.add_argument("--walk", help="walk", action="store_true")
    parser.add_argument("--dump", help="dump", action="store_true")
    return parser.parse_args()

def mkdir_soft(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

def process(g):
    """
    Partitions and refines our graph :g, and prints some nice stats about it.
    """
    # print("hey, p = %s" % type(p))
    # r = refine_partition(p)
    r = g.partition().refine()
    rows,total = describe_partition(r)
    print(tabulate(rows,headers="firstrow"))
    print("Making for %d components total." % total['component'])
    # for tag in sorted(r.keys()):
    #     print("class[%s] = %s" % (tag,{x:len(r[tag][x]) for x in r[tag]}))
    return r


def walk(r,clone=False):
    """Performs an ordered traversal of a refined partition :r, yielding a seguence
    of OrderedDict structs keyed on the fields ('cat','dims','seq','edges'), where each
    dict corresponds to a component in our forest.  [Need to explain these fields].

    If an optional :clone flag is provided, we clone (deepcopy) the edge list on
    the way out.  (Which is safer, because otherwise our edgelists would be members
    embedded in our partition struct somewhere, but at performance cost of course).
    """
    for k,category in r.items():
        for t in sorted(category.keys()):
            for i,edges in enumerate(category[t]):
                if clone:
                    edges = copy.deepcopy(edges)
                items = [('cat',k),('dims',t),('seq',i+1),('edges',edges)]
                yield OrderedDict(items)


def dumpall(outdir,tag,r):
    category = r[tag]
    subdir = "%s/%s" % (outdir,tag);
    mkdir_soft(outdir)
    mkdir_soft(subdir)
    _pl = 'es' if len(category) > 1 else '';
    print("extracting category '%s' with %d component class%s .." % (tag,len(category),_pl))
    for t in sorted(category.keys()):
        nj,nk = t
        components = category[t]
        # print ("class[%s] = has %d component(s):" % (t,len(components)))
        for i,g in enumerate(components):
            basefile = "%d,%d-%d.txt" % (nj,nk,i)
            outpath = "%s/%s" % (subdir,basefile)
            # print("%s .." % outpath)
            edgelist = sorted(g.edges())
            with open(outpath,"wt") as f:
                ezbpg.ioutil.save_edges(f,edgelist)

def main():
    args = parse_args()

    g = ezbpg.slurp(args.infile)
    print("Consumed %d edge observations, of which %d were distinct." % (g.observed,g.distinct))
    # print("stats = ",json.dumps(g.stats(),sort_keys=True))
    r = process(g)

    outdir = 'comp'
    if args.dump:
        tags = sorted(r.keys())
        for tag in tags:
            dumpall(outdir,tag,r)

    if args.stroll:
        for r in walk(r,clone=True):
            # We can -almost- just print our dicts as-is, except for the possibly
            # very long edge lists.  So we make a quick substitution:
            edges = r['edges']
            n = len(edges)
            _pl = 's' if n > 1 else ''
            r['edges'] = "[%d edge%s]" % (n,_pl)
            print(r)

    print("done")

if __name__ == '__main__':
    main()



