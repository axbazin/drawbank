#!/usr/bin/env python3
#coding:utf-8

# Author: Adelme Bazin

#default libraries
import argparse
import sys
from collections import Counter, defaultdict
import pkg_resources

#installed library
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def get_most_numerous(all_spe, m):
    """returns year-per-year counts for the m most numerous species"""
    d = Counter()
    for spe, count in all_spe.items():
        tot = sum([ val for val in count.values()])
        d[spe] = tot
    species = [ data[0] for data in d.most_common(m)]
    num_spe = {}
    for spe in species:
        num_spe[spe] = all_spe[spe]
    return num_spe

def parse_assembly(fname):
    """parses the assembly summary to produce year-per-year counts for each species and in total"""
    most_n_spe = defaultdict(Counter)
    years = Counter()
    nb_no_date = 0
    with open(fname, "r") as f:
        for line in f:
            if not line.startswith("#"):
                linedata = line.split("\t")
                if linedata[14] == "":
                    nb_no_date+=1
                else:
                    curr_y = int(linedata[14].split('/')[0])
                    most_n_spe[linedata[7]][curr_y] +=1#should use species taxid instead (+ ete3)
                    years[curr_y]+=1
    if nb_no_date > 0:
        print(f"WARNING: {nb_no_date} genomes had no date of submission in your assembly summary.")
    return most_n_spe, years

def cmdline():
    """
        Functions that defines the command line arguments.
    """
    parser = argparse.ArgumentParser(description = "Draws the current number of genomes in GenBank, with the given filters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    fig = parser.add_argument_group(title= "Figure")
    fig.add_argument('-m', '--most_numerous_species', required=False, type=int ,default=0, help="Indicate the n most numerous species")
    fig.add_argument('-g','--groups', required=False, type=str, default="all", help="Different groups that you want included in your figure, separated by a ','")
    fig.add_argument("-c", "--cumulative", default=False, required=False, action="store_true", help="make a cumulative bar chart rather than have each year's addition")
    outlog = parser.add_argument_group(title = "Output and formating")
    outlog.add_argument('-f', "--formats", required=False, type=str.lower, default="html", help="Different formats that you want as output, separated by a ','")
    outlog.add_argument("--basename", required=False, type=str, help="Basename to use for output files")

    misc = parser.add_argument_group(title = "Misc options")
    misc.add_argument("--assembly", required=False, type=str, help = "An assembly summary to use (if not provided, will download the latest one automatically)")
    # misc.add_argument("--cpu", required=False, type=int, default=1, help="Number of cpus to use.")
    misc.add_argument("--verbose", required=False, action="store_true", default=False, help="show the DEBUG log")
    misc.add_argument('--version', action='version', version='%(prog)s ' + pkg_resources.get_distribution("drawbank").version)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

def make_df(years, most_numerous, cumulative=True):
    """Creates the pandas dataframe"""
    d = defaultdict(list)
    for y in range(min(years.keys()), max(years.keys())+1):
        y_rest = years.get(y,0)
        for spe in most_numerous.keys():
            spe_y_count = most_numerous[spe].get(y, 0)
            y_rest -= spe_y_count
            d["species"].append(spe)
            d["year"].append(y)
            d["count"].append(spe_y_count)
            if cumulative and len(d["count"]) > len(most_numerous)+1:
                d["count"][-1] += d["count"][-(len(most_numerous)+2)]
        d["species"].append("Others")
        d["year"].append(y)
        d["count"].append(y_rest)
        if cumulative and len(d["count"]) > len(most_numerous)+1:
            d["count"][-1] += d["count"][-(len(most_numerous)+2)]
    return pd.DataFrame.from_dict(d)


def main():
    args = cmdline()
    if args.assembly is None:
        raise NotImplementedError()
        #download assembly summary

    all_species, years = parse_assembly(args.assembly)
    most_numerous = get_most_numerous(all_species, args.most_numerous_species)

    df = make_df(years, most_numerous, cumulative = args.cumulative)
    title = ""
    if args.cumulative:
        title += "Cumulative "
    title += "Genbank genome count per year"
    fig = px.bar(df, x="year",y="count",color="species", title = title)

    fig.show()

    print("Drawing is done. It should be opened in your system's default browser.")



if __name__ == "__main__":
    main()