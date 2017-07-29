from ezbpg.ioutil import purify, csviter
from ezbpg.core import BipartiteGraph

def ingest(edgeseq):
    return BipartiteGraph(edgeseq)

def slurp(path):
    edgeseq = purify(csviter(path))
    return ingest(edgeseq)

