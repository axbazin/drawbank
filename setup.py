#!/usr/bin/env python3

#default libraries
import setuptools
import os

if __name__ == "__main__":
    setuptools.setup(
        name="drawbank",
        version=open(os.path.join(os.path.dirname(__file__), "VERSION")).read().rstrip(),
        # url="https://github.com/axbazin/synta",
        description="Draws the current number of available genomes in GenBank",
        packages=setuptools.find_packages(),
        classifiers=["Environment :: Console",
                "Intended Audience :: Science/Research",
                "License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)",
                "Natural Language :: English",
                "Operating System :: POSIX :: Linux",
                "Programming Language :: Python :: 3",
                "Topic :: Scientific/Engineering :: Bio-Informatics"],
        entry_points={"console_scripts":["drawbank = drawbank.drawbank:main"]},
    )