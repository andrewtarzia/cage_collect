#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Distributed under the terms of the MIT License.

"""
Script to collate the window sizes of all cages of all CIFs.

Author: Andrew Tarzia

Date Created: 02 Jan 2020
"""

import sys
import logging
import json


def main():
    if (not len(sys.argv) == 4):
        print("""
    Usage: collate_window_sizes.py string window_outfile pore_outfile
        string (str) :
            string to use to search for JSON files to collect data from
            [*.json should be part of this search string]
        window_outfile (str) :
            file to output window data too (should be a csv file, will
            be overwritten)
        pore_outfile (str) :
            file to output pore data too (should be a csv file, will
            be overwritten)
        """)
        sys.exit()
    if '*' in sys.argv[1]:
        from glob import glob
        jsons = sorted([i for i in glob(sys.argv[1])])
        logging.info(f'{len(jsons)} jsons to analyze')
    else:
        jsons = [sys.argv[1]]
    window_outfile = sys.argv[2]
    pore_outfile = sys.argv[3]

    final_output = {}

    for file in jsons:
        with open(file, 'rb') as f:
            data = json.load(f)

        REFCODE = file.split('_')[0]
        cage_no = file.rstrip('.json').split('_')[-1]
        windows = data['windows']['diameters']
        pores = data['pore_diameter_opt']['diameter']

        final_output[file] = {
            'ref': REFCODE,
            'cage_no': cage_no,
            'windows': windows,
            'pores': pores
        }

    with open(window_outfile, 'w') as f:
        top_line = 'filename,REFCODE,cage_no,window_diams\n'
        f.write(top_line)
        for file in final_output:
            d = final_output[file]
            window_string = ','.join([str(i) for i in d['windows']])
            out_line = (
                f"{file},{d['ref']},{d['cage_no']},{window_string}\n"
            )
            f.write(out_line)

    with open(pore_outfile, 'w') as f:
        top_line = 'filename,REFCODE,cage_no,pore_diam\n'
        f.write(top_line)
        for file in final_output:
            d = final_output[file]
            out_line = (
                f"{file},{d['ref']},{d['cage_no']},{d['pores']}\n"
            )
            f.write(out_line)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='')
    main()
