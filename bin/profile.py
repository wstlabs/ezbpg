#!/usr/bin/env python
import sys, argparse
import simplejson as json
from tabulate import tabulate
from bipartite.random  import generate 
from bipartite.utils   import csviter, purify
from bipartite.matcher import Matcher, partition_forest, refine_partition, describe_partition

parser = argparse.ArgumentParser()
parser.add_argument("--csvfile", help="csv file to parse")
parser.add_argument("--random", help="parameters(n,m,r) to generate a random graph from")
args = parser.parse_args()

if args.csvfile:
    edgeseq = purify(csviter(args.csvfile))
elif args.random:
    argv = args.random.split(',') 
    if len(argv) < 3:
        raise ValueError("need exactly 3 comma-separated paramters")
    m,n,r = tuple(int(t) for t in argv)
    edgeseq = generate(m,n,limit=r)
else: 
    edgeseq = generate(10,8,limit=15)


g = Matcher(edgeseq)
print("Consumed %d edge observations, of which %d were distinct." % (g.observed,g.distinct))
print("stats = ",json.dumps(g.stats(),sort_keys=True))
print("valhist = ",json.dumps(g.valhist(),sort_keys=True))

p = partition_forest(g)
r = refine_partition(p)
rows,total = describe_partition(r)
print(tabulate(rows,headers="firstrow"))

print("Making for %d components total." % total['component'])
for tag in sorted(r.keys()):
    print("class[%s] = %s" % (tag,{x:len(r[tag][x]) for x in r[tag]})) 


#
# r = dict->dict->list[tuple(int,int)]
# r[category-tag][component-class]
#

tag = 'm-n'
print("tag '%s' has %d component class(es)." % (tag,len(r[tag])))
for x in sorted(r[tag].keys()):
    components = r[tag][x]
    print ("class[%s] = has %d component(s):" % (x,len(components)))
    # for i,y in enumerate(components):
    #    print("component[%d] = %s" % (i,y))

sys.exit(1)

