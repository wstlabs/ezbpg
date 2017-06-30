import codecs

def cleaniter(filename,encoding):
    with codecs.open(filename,"r",encoding) as f:
        for line in f:
            clean = line.rstrip()
            if len(clean):
                yield clean

def csviter(filename,encoding=None):
    for line in cleaniter(filename,encoding):
        yield tuple(line.rstrip().split(','))

def purify(tupseq):
    for x,y in tupseq:
        if x is not None and y is not None: 
            yield x,y


def save_edges(f,edgeseq):
    for edge in edgeseq:
        f.write("%s,%s\n" % edge)

