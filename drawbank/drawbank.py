#!/usr/bin/env python3
#coding:utf-8

# Author: Adelme Bazin

#default libraries
import argparse
import sys
import os
from collections import Counter, defaultdict
import pkg_resources
import logging
import requests
import datetime
from dateutil.parser import parse as parsedate

#installed library
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from appdirs import user_cache_dir


TAXONOMIC_GROUPS = ["all","archaea","bacteria","fungi","invertebrate","metagenomes","plant","protozoa","vertebrate_mammalian","viral","vertebrate_other","other"]

def get_most_numerous(all_spe, m):
    """returns year-per-year counts for the m most numerous group"""
    logging.getLogger().info(f"Filtering the {m} most common group")
    d = Counter()
    for spe, count in all_spe.items():
        tot = sum([ val for val in count.values()])
        d[spe] = tot
    group = [ data[0] for data in d.most_common(m)]
    num_spe = {}
    for spe in group:
        num_spe[spe] = all_spe[spe]
    return num_spe

def parse_assembly(fnames):
    """parses one or more assembly summary to produce year-per-year counts for each group and in total"""
    if len(fnames) == 1:
        logging.getLogger().info("Parsing assembly file")
    else:
        logging.getLogger().info(f"Parsing {len(fnames)} assembly files")
    n_spe = defaultdict(Counter)
    years = Counter()
    nb_no_date = 0
    for fname in fnames:
        with open(fname, "r") as f:
            for line in f:
                if not line.startswith("#"):
                    linedata = line.split("\t")
                    if linedata[14] == "":
                        nb_no_date+=1
                    else:
                        curr_y = int(linedata[14].split('/')[0])
                        n_spe[linedata[7]][curr_y] +=1#should use group taxid instead (+ ete3)
                        years[curr_y]+=1
    if nb_no_date > 0:
        logging.getLogger().warning(f"{nb_no_date} genomes had no date of submission in your assembly summary.")
    return n_spe, years

def make_df(years, most_numerous, cumulative=True):
    """Creates the pandas dataframe to generate the figure"""
    d = defaultdict(list)
    for y in range(min(years.keys()), max(years.keys())+1):
        y_rest = years.get(y,0)
        for spe in most_numerous.keys():
            spe_y_count = most_numerous[spe].get(y, 0)
            y_rest -= spe_y_count
            d["group"].append(spe)
            d["year"].append(y)
            d["count"].append(spe_y_count)
            if cumulative and len(d["count"]) > len(most_numerous)+1:
                d["count"][-1] += d["count"][-(len(most_numerous)+2)]
        d["group"].append("Others")
        d["year"].append(y)
        d["count"].append(y_rest)
        if cumulative and len(d["count"]) > len(most_numerous)+1:
            d["count"][-1] += d["count"][-(len(most_numerous)+2)]
    return pd.DataFrame.from_dict(d)

def make_urls(section, taxons):
    uri = 'https://ftp.ncbi.nih.gov/genomes'
    urls = set()
    CACHE_DIR = user_cache_dir(appname="drawbank", appauthor="axbazin")

    for tax in taxons:
        if tax == "all":
            urls.add((f"{uri}/{section}/assembly_summary_{section}.txt", f"{CACHE_DIR}/{section}_assembly_summary.txt"))
        else:
            urls.add((f"{uri}/{section}/{tax}/assembly_summary.txt", f"{CACHE_DIR}/{section}_{tax}_assembly_summary.txt"))
    return urls

def get_summaries(section, taxons, no_cache):
    summaries = set()
    for url, dest_file in make_urls(section, taxons):
        r = requests.head(url)
        url_time = r.headers['last-modified']
        url_date = parsedate(url_time)
        download_file = True
        if os.path.exists(dest_file) and not no_cache:
            if url_date <= datetime.datetime.fromtimestamp(os.path.getmtime(dest_file), tz= datetime.timezone.utc):
                download_file = False

        if download_file:
            logging.getLogger().info(f"Downloading {section} summary file from: {url}")
            if not os.path.exists(os.path.dirname(dest_file)):
                os.mkdir(os.path.dirname(dest_file))
            with open(dest_file,"w") as dfs:
                dfs.write(requests.get(url).text)
            os.utime(dest_file ,(int(url_date.timestamp()), int(url_date.timestamp())))
        else:
            logging.getLogger().info(f"Using cached file: {dest_file}")
        summaries.add(dest_file)

    return summaries

def get_taxonomic_groups(groups):
    taxons = groups.split(",")
    for tax in taxons:
        if tax not in TAXONOMIC_GROUPS:
            raise Exception(f"{tax} is not a known subdivision of genbank (or refseq). Please use any of {','.join(TAXONOMIC_GROUPS)}")

    return taxons

def cmdline():
    """
        Functions that defines the command line arguments.
    """
    parser = argparse.ArgumentParser(description = "Draws the current number of genomes in GenBank, with the given filters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    fig = parser.add_argument_group(title= "Figure")
    fig.add_argument('-m', '--most_numerous_group', required=False, type=int ,default=5, help="Indicate the n most numerous group")
    fig.add_argument("-c", "--cumulative", default=False, required=False, action="store_true", help="make a cumulative bar chart rather than have each year's addition")
    dat = parser.add_argument_group(title = "Data source")
    dat.add_argument('-s', "--section", required=False, type=str.lower, default="genbank", choices=["genbank","refseq"], help="Section to download from")
    dat.add_argument("-g","--group", required=False, type=str.lower, default="all", help=f"comma separated list of groups to download from (any value among {','.join(TAXONOMIC_GROUPS)})")
    dat.add_argument("-N","--no_cache", required=False, action="store_true", default=False, help = "Do not cache downloaded files (nor use cached files).")
    misc = parser.add_argument_group(title = "Misc options")
    misc.add_argument("--assembly", required=False, type=str, help = "An assembly summary to use (if not provided, will download the latest one automatically)")
    misc.add_argument("--verbose", required=False, action="store_true", default=False, help="show the DEBUG log")
    misc.add_argument('--version', action='version', version='%(prog)s ' + pkg_resources.get_distribution("drawbank").version)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()

def main():
    args = cmdline()

    if args.verbose:
        level = logging.DEBUG#info, debug, warnings and errors
    else:
        level = logging.INFO#info, warnings and errors
    logging.basicConfig(stream=sys.stdout, level = level, format = '%(asctime)s %(filename)s:l%(lineno)d %(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().info("Command: "+" ".join([arg for arg in sys.argv]))
    logging.getLogger().info("drawbank version: "+pkg_resources.get_distribution("drawbank").version)

    summaries = set()
    if args.assembly is None:
        taxons = get_taxonomic_groups(args.group)
        summaries |= get_summaries(args.section, taxons, no_cache = args.no_cache)
    else:
        summaries.add(args.assembly)

    all_group, years = parse_assembly(summaries)
    most_numerous = get_most_numerous(all_group, args.most_numerous_group)

    df = make_df(years, most_numerous, cumulative = args.cumulative)
    title = ""
    if args.cumulative:
        title += "Cumulative "
    title += "Genbank genome count per year"

    fig = px.bar(df, x="year",y="count",color="group", title = title)
    logging.getLogger().info("Drawing figure...")
    fig.show()

    logging.getLogger().info("Drawing is done. Figure should be opened in your system's default browser.")



if __name__ == "__main__":
    main()