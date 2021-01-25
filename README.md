# drawbank
This is a small tool that helps to draw the current genbank or refseq genome count through time, indicating the most common species  and filtering down on specific groups if need be.



# Installation

you can clone the git repository, go to its root and run:

`python setup.py install`

or

`pip install .`

This will install dependencies and the command line tool.

# Quick usage

`drawbank` can be called with or without options. It will download the latest assembly summary, or use the one provided through the command line. By default it will display the number of genomes added each year. 

![Genbank genome count](https://github.com/axbazin/drawbank/raw/master/img/Genbank_genomes_noncumulative_012521.png)


To see the more usual 'cumulative count of genomes added each year", you can do it as such:

`drawbank -c`

 draw something akin to this (it was drawn in early 2021 which is why 2020 and 2021 look alike), and display it in your browser.

![Cumulative genbank genome counts](https://github.com/axbazin/drawbank/raw/master/img/GenBank_genome_count_012521.png)

You can filter down to any group of interest, for example looking only at plants:

`drawbank -c -g plants`

![Cumulative genbank plant genome count](https://github.com/axbazin/drawbank/raw/master/img/GenBank_plants_count_012521.png)

# Command line options

All options can be viewed using `drawbank -h`:

```
usage: drawbank [-h] [-m MOST_NUMEROUS_GROUP] [-c] [-s {genbank,refseq}] [-g GROUP] [-N] [--assembly ASSEMBLY] [--verbose] [--version]

Draws the current number of genomes in GenBank, with the given filters

optional arguments:
  -h, --help            show this help message and exit

Figure:
  -m MOST_NUMEROUS_GROUP, --most_numerous_group MOST_NUMEROUS_GROUP
                        Indicate the n most numerous group (default: 5)
  -c, --cumulative      make a cumulative bar chart rather than have each year's addition (default: False)

Data source:
  -s {genbank,refseq}, --section {genbank,refseq}
                        Section to download from (default: genbank)
  -g GROUP, --group GROUP
                        comma separated list of groups to download from (any value among
                        all,archaea,bacteria,fungi,invertebrate,metagenomes,plant,protozoa,vertebrate_mammalian,viral,vertebrate_other,other) (default: all)
  -N, --no_cache        Do not cache downloaded files (nor use cached files). (default: False)

Misc options:
  --assembly ASSEMBLY   An assembly summary to use (if not provided, will download the latest one automatically) (default: None)
  --verbose             show the DEBUG log (default: False)
  --version             show program's version number and exit
  ```

# Dependencies

They are all listed in the requirements.txt file.

- python>=3.6
- plotly>=4.0
- appdirs
- requests
- ete3>=3.0
- python-dateutil
- pandas



