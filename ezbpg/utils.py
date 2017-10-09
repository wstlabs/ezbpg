import os, sys
from tabulate import tabulate
import ioany

"""
A nifty module of nifty support functions.
"""

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
                ezbpg.ioutil.save_edges(f,edgelist)

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


"""
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", help="csv file to parse", required=True)
    parser.add_argument("--stroll", help="stroll", action="store_true")
    parser.add_argument("--stroll2", help="stroll2", action="store_true")
    parser.add_argument("--walk", help="walk", action="store_true")
    parser.add_argument("--dump", help="dump", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()

    g = ezbpg.slurp(args.infile)
    print("Consumed %d edge observations, of which %d were distinct." % (g.observed,g.distinct))
    r = process(g)

    outdir = 'comp'
    if args.dump:
        dumpall(outdir,r)
        project(outdir,r)

    if args.stroll:
        for d in stroll(r):
            print(d)

    if args.stroll2:
        stroll_over(r)

    print("done")

if __name__ == '__main__':
    main()



def mkdir_soft(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
"""

