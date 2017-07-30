import copy
import os, sys, argparse
import simplejson as json
from collections import OrderedDict
from tabulate import tabulate
import ezbpg
# from ezbpg.core import describe_partition

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
    r = g.partition().refine()
    rows,total = r.describe()
    print(tabulate(rows,headers="firstrow"))
    print("Making for %d components total." % total['component'])
    return r

def dumpfor(outdir,tag,category):
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

def dumpall(outdir,r):
    for tag,catiter in r.walk2():
        pass

def stroll(r):
    for d in r.walk():
        # We can -almost- just print our dicts as-is, except for the possibly
        # very long edge lists.  So we make a quick substitution:
        n = len(d['graph'])
        _pl = 's' if n > 1 else ''
        d['graph'] = "[%d edge%s]" % (n,_pl)
        yield d

def main():
    args = parse_args()

    g = ezbpg.slurp(args.infile)
    print("Consumed %d edge observations, of which %d were distinct." % (g.observed,g.distinct))
    r = process(g)

    outdir = 'comp'
    if args.dump:
        for tag,category in r:
            dumpfor(outdir,tag,category)

    if args.stroll:
        for d in stroll(r):
            print(d)

    print("done")

if __name__ == '__main__':
    main()






#
# Deprecated Stuff 
#
def __walk(r):
    """Performs an ordered traversal of a refined partition :r, yielding a seguence
    of OrderedDict structs keyed on the fields ('cat','dims','seq','edges'), where each
    dict corresponds to a component in our forest.  [Need to explain these fields].
    """
    for k,category in r:
        for t in sorted(category.keys()):
            for i,edges in enumerate(category[t]):
                items = [('cat',k),('dims',t),('seq',i+1),('edges',edges)]
                yield OrderedDict(items)

