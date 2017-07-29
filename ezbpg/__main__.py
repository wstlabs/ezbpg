import os, sys, argparse
import simplejson as json
from tabulate import tabulate
import ezbpg
import ezbpg.ioutil as ioutil
from ezbpg.matcher import partition_forest, refine_partition, describe_partition

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", help="csv file to parse", required=True)
    return parser.parse_args()

def mkdir_soft(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

def process(g):
    """
    Partitions and refines our graph :g, and prints some nice stats about it.
    """
    p = partition_forest(g)
    r = refine_partition(p)
    rows,total = describe_partition(r)
    print(tabulate(rows,headers="firstrow"))
    print("Making for %d components total." % total['component'])
    # for tag in sorted(r.keys()):
    #     print("class[%s] = %s" % (tag,{x:len(r[tag][x]) for x in r[tag]}))
    return r

def extract(outdir,tag,r):
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
        for i,edgelist in enumerate(components):
            basefile = "%d,%d-%d.txt" % (nj,nk,i)
            outpath = "%s/%s" % (subdir,basefile)
            # print("%s .." % outpath)
            with open(outpath,"wt") as f:
                ioutil.save_edges(f,edgelist)

def main():
    args = parse_args()

    g = ezbpg.slurp(args.infile)
    print("Consumed %d edge observations, of which %d were distinct." % (g.observed,g.distinct))
    # print("stats = ",json.dumps(g.stats(),sort_keys=True))
    r = process(g)

    outdir = 'comp'
    tags = sorted(r.keys())
    for tag in tags:
        extract(outdir,tag,r)
    print("done")

if __name__ == '__main__':
    main()



