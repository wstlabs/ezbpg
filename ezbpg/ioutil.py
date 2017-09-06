
def cleaniter(path,encoding='utf-8'):
    with open(path,"rtU",encoding=encoding) as f:
        for line in f:
            clean = line.rstrip()
            if len(clean):
                yield clean

def csviter(path,encoding='utf-8'):
    for line in cleaniter(path,encoding):
        yield tuple(line.rstrip().split(','))

def purify(tupseq):
    for t in tupseq:
         # We do this check because from time to time we ingest tuples that either come 
         # from CSV files that are themselves dirty (e.g not strictly 2 columns), or the
         # CSV parser has been incorrectly configured (to not recognize quote lines with 
         # embedded commas, for example).
        if len(t) != 2:
            raise ValueError("invalid tuple length")
        x,y = t
        if x is not None and y is not None:
            yield x,y

def save_edges(f,edgeseq):
    for edge in edgeseq:
        f.write("%s,%s\n" % edge)

