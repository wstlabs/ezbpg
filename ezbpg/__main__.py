import argparse
import ezbpg

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", help="csv file to parse", required=True)
    parser.add_argument("--stroll", help="stroll", action="store_true")
    parser.add_argument("--export", type=str, required=False, help="optional output directory for data dumps")
    return parser.parse_args()


def main():
    args = parse_args()

    g = ezbpg.read_csv(args.infile)
    print(f"Our graph has {g.tally.caption}")
    r = g.partition().refine() 
    print(r.survey.describe())
    count = r.survey.total['component']
    pl = "" if count == 1 else "s" 
    print(f"With {count} component{pl} total")

    if args.outdir:
        r.extract_categories(args.outdir)

    if args.stroll:
        for info in r.walk():
            print(info.caption)

    print("all done")

if __name__ == '__main__':
    main()


