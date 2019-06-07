#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Distributed under the terms of the MIT License.

"""
Script to test the shape persistency of a cage molecule.

1 - run full pyWindow analysis
2 - extract all independant cages
3 - run energy minimization/MD on independant cages
    optimization method can be swapped out. Default is OPLS3 with macromodel
4 - rerun pyWindow analysis to determine shape persistency

Author: Andrew Tarzia

Date Created: 22 Mar 2019

"""

import sys
import os
import glob
import matplotlib.pyplot as plt
import json
import pywindow as pw
import atools


def main():
    if (not len(sys.argv) == 1):
        print("""
Usage: test_shape.py
    """)
        sys.exit()
    else:
        pass

    # get CIFs of interest -- cleaned if it exists, otherwise original
    list_of_cifs = [i for i in glob.glob('*.cif') if '_cleaned' not in i]
    list_of_cleaned_cifs = glob.glob('*_cleaned.cif')
    calculation_list = [i for i in list_of_cifs
                        if i.replace('.cif', '_cleaned.cif') not in list_of_cleaned_cifs]
    for i in list_of_cleaned_cifs:
        calculation_list.append(i)
    for calc in calculation_list:
        print(calc)
        pre_op = calc.replace('.cif', '_preop')
        pdb_file = calc.replace('.cif', '.pdb')
        print(pdb_file, pre_op)
        if os.path.isfile(pdb_file) is False:
            pdb_file, _ = atools.convert_CIF_2_PDB(calc)
            if pdb_file is None and _ is None:
                continue
            del _  # we don't need the ASE structure in this case
        # rebuild system
        rebuilt_structure = atools.modularize(file=pdb_file)
        if rebuilt_structure is None:
            # handle pyWindow failure
            sys.exit(f'pyWindow failure on {pdb_file}')
        # run analysis on rebuilt system (extracts all cages)
        _ = atools.analyze_rebuilt(rebuilt_structure,
                                   file_prefix=pre_op,
                                   atom_limit=20,
                                   include_coms=False,
                                   verbose=False)
        del _  # not needed
        # determine independant cages based on pore diameters
        # actually, at this stage we just optimize all of them
        indep_cages = {}
        for js in glob.glob(pre_op + '*.json'):
            with open(js, 'r') as f:
                data = json.load(f)
            # if data['pore_diameter_opt']['diameter'] > 0:
            ID = js.rstrip('.json')
            indep_cages[ID] = data['pore_diameter_opt']['diameter']
        print(indep_cages)
        # check shape persistency of each independant cage
        cage_output = {}
        for ID in indep_cages:
            newID = ID.replace('preop', 'postop')
            # run MD with OPLS if output file does not exist
            if os.path.isfile(newID + '.pdb') is False:
                print('doing optimization of cage:', ID)
                atools.optimize_structunit(
                    infile=ID + '.pdb',
                    outfile=newID + '.pdb',
                    exec='/home/atarzia/software/schrodinger_install',
                    method='OPLS',
                    settings=atools.atarzia_long_MD_settings())
                print('done')
            # analyze optimized cage with pyWindow and output to JSON
            if os.path.isfile(newID + '.json') is False:
                cagesys = pw.MolecularSystem.load_file(newID + '.pdb')
                cage = cagesys.system_to_molecule()
                atools.analyze_cage(cage=cage,
                                    propfile=newID + '.json',
                                    structfile=None)
            with open(newID + '.json', 'r') as f:
                data = json.load(f)
            new_pore_diam = data['pore_diameter_opt']['diameter']
            cage_output[newID] = (indep_cages[ID], new_pore_diam)
            print('-----------------------------------------')
            print(ID, newID)
            print('preop diameter:', indep_cages[ID])
            print('postop diameter:', new_pore_diam)
            print('-----------------------------------------')
        # output plot for each CIF
        plotx = [cage_output[i][0] for i in cage_output]
        ploty = [cage_output[i][1] for i in cage_output]
        fig, ax = atools.parity_plot(
            X=plotx, Y=ploty,
            xtitle='XRD pore diameter [$\mathrm{\AA}$]',
            ytitle='opt. pore diameter [$\mathrm{\AA}$]',
            lim=(0, round(max([max(ploty), max(plotx)])) + 1),
        )
        fig.tight_layout()
        fig.savefig(calc.replace('.cif', '.pdf'), dpi=720,
                    bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    main()
