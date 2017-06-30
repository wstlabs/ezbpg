#!/usr/bin/env python
import os, sys, argparse
import simplejson as json
from tabulate import tabulate
from bipartite.utils   import csviter, purify, save_edges
from bipartite.matcher import Matcher, partition_forest, refine_partition, describe_partition

parser = argparse.ArgumentParser()
parser.add_argument("--csvfile", help="csv file to parse", required=True)
args = parser.parse_args()

edgeseq = purify(csviter(args.csvfile))

g = Matcher(edgeseq)
print("Consumed %d edge observations, of which %d were distinct." % (g.observed,g.distinct))
print("stats = ",json.dumps(g.stats(),sort_keys=True))

p = partition_forest(g)
r = refine_partition(p)
rows,total = describe_partition(r)
print(tabulate(rows,headers="firstrow"))

print("Making for %d components total." % total['component'])
for tag in sorted(r.keys()):
    print("class[%s] = %s" % (tag,{x:len(r[tag][x]) for x in r[tag]}))


tag = 'm-n'
outdir = "comp/%s" % tag
if not os.path.exists(outdir):
    os.mkdir(outdir)
print("tag '%s' has %d component class(es)." % (tag,len(r[tag])))
for t in sorted(r[tag].keys()):
    nj,nk = t
    components = r[tag][t]
    print ("class[%s] = has %d component(s):" % (t,len(components)))
    for i,edgelist in enumerate(components):
        basefile = "%d,%d-%d.txt" % (nj,nk,i)
        outpath = "%s/%s" % (outdir,basefile)
        print("%s .." % outpath)
        with open(outpath,"wt") as f:
            save_edges(f,edgelist)


