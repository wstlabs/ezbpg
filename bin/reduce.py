#!/usr/bin/env python
import argparse
import simplejson as json
from bipartite.utils   import csviter, purify
from bipartite.matcher import Matcher
from bipartite.extras import prune_trails

parser = argparse.ArgumentParser()
parser.add_argument("--csvfile", help="csv file to parse", required=True)
args = parser.parse_args()

edgeseq = purify(csviter(args.csvfile))

g = Matcher()
g.consume(edgeseq)
print("Consumed %d edge observations, of which %d were distinct." % (g.observed,g.distinct))
print("stats = ",json.dumps(g.stats(),sort_keys=True))
print("valhist = ",json.dumps(g.valhist(),sort_keys=True))

print("prune ..")
n = prune_trails(g)
print("Pruned %d leaves; gives us %d distinct." % (n,g.distinct))
print("stats = ",json.dumps(g.stats(),sort_keys=True))
print("valhist = ",json.dumps(g.valhist(),sort_keys=True))

