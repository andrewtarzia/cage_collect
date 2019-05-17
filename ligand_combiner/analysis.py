#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Distributed under the terms of the MIT License.

"""
Module of functions used to analyze all built molecules from DB of core,
ligands and linkers.

Author: Andrew Tarzia

Date Created: 17 Apr 2019

"""

import sys
import numpy as np
import logging
import matplotlib.pyplot as plt
import matplotlib.cm as cm
sys.path.insert(0, '/home/atarzia/thesource/')
import Combiner
import plotting
import calculations


def analyze_conformer_NNdist(stk_mol, name):
    '''Plot a distribution of the NN distance for a given molecule and all of its
    conformers.

    '''
    NN_dists = []
    conformers = range(stk_mol.mol.GetNumConformers())
    for cid in conformers:
        NN_dists.append(np.linalg.norm(stk_mol.geom_prop[cid]['NN_v']))
    fig, ax = plotting.histogram_plot_1(Y=NN_dists, X_range=(4, 20), width=0.2,
                                        alpha=1.0, color='#64B5F6',
                                        edgecolor='k',
                                        xtitle='NN distance [$\mathrm{\AA}$]')

    fig.tight_layout()
    fig.savefig(name+'_NN_dists.pdf', dpi=720,
                bbox_inches='tight')
    plt.close()


def analyze_conformer_angles(stk_mol, name):
    '''Plot a distribution of the interior angles for a given molecule and all of its
    conformers.

    '''
    angles = []
    conformers = range(stk_mol.mol.GetNumConformers())
    for cid in conformers:
        angles.append(stk_mol.geom_prop[cid]['NN_BCN_1'])
        angles.append(stk_mol.geom_prop[cid]['NN_BCN_2'])
    fig, ax = plotting.histogram_plot_1(Y=angles, X_range=(0, 180), width=2,
                                        alpha=1.0, color='#64B5F6',
                                        edgecolor='k',
                                        xtitle='angles [degrees]')

    fig.tight_layout()
    fig.savefig(name+'_angle_dists.pdf', dpi=720,
                bbox_inches='tight')
    plt.close()


def analyze_conformer_energies(stk_mol, name):
    '''Calculate the energy of all conformers in stk_molecule using UFF and
    GFN2-xTB.

    '''
    UFF_energies = []
    dihedrals = []
    GFN_energies = []
    marks = []
    conformers = range(stk_mol.mol.GetNumConformers())
    for cid in conformers:
        UFF_energy = Combiner.get_energy(stk_mol=stk_mol,
                                         conformer=cid, FF='UFF')
        UFF_energies.append(UFF_energy)
        # GFN_energy = GETGFNENERGY(stk_mol=stk_mol,
        #                           conformer=cid, FF='GFN')
        GFN_energy = 0
        GFN_energies.append(GFN_energy)
        # calculate the dihedral between N1 - liga1_com - liga2_com - N2
        NBBN_dihed = calculations.get_dihedral(
            pt1=stk_mol.geom_prop[cid]['liga1']['N_pos'],
            pt2=stk_mol.geom_prop[cid]['liga1']['pos'],
            pt3=stk_mol.geom_prop[cid]['liga2']['pos'],
            pt4=stk_mol.geom_prop[cid]['liga2']['N_pos'])
        dihedrals.append(abs(NBBN_dihed))
        if Combiner.check_binder_directions(mol=stk_mol, cid=cid):
            marks.append('x')
        else:
            marks.append('o')
    rel_UFF = [i-min(UFF_energies) for i in UFF_energies]
    rel_GFN = [i-min(GFN_energies) for i in GFN_energies]

    # UFF_range = (round(min(UFF_energies)-0.1*min(UFF_energies)),
    #              round(max(UFF_energies)+0.1*max(UFF_energies)))
    # GFN_range = (round(min(GFN_energies)-0.1*min(GFN_energies)),
    #              round(max(GFN_energies)+0.1*max(GFN_energies)))
    UFF_range = (0, max(rel_UFF)+0.2*max(rel_UFF))
    GFN_range = (0, max(rel_GFN)+0.2*max(rel_GFN))
    # plot scatter plots of energies on y axis, dihedrals on x axis
    # include XRD energy as horiz line
    fig, ax = plotting.scatter_plot(X=dihedrals, Y=rel_UFF,
                                    ytitle='relative UFF energy [kJ/mol]',
                                    xtitle='NLLN dihedral [degrees]',
                                    ylim=UFF_range,
                                    xlim=(-10, 200),
                                    c='#64B5F6', alpha=0.8,
                                    edgecolors='none',
                                    marker='o')

    # add lines for UFF energy of XRD ligands
    UFF_XRD_energies = get_clever_XRD_energies(FF='UFF')[name]
    UFF_XRD_energies = [i-min(UFF_energies) for i in UFF_XRD_energies]
    ax.axhline(y=min(UFF_XRD_energies), c='k', linestyle='--')
    ax.axhline(y=max(UFF_XRD_energies), c='k', linestyle='--')
    # do dihedral limits
    ax.axvline(x=20, c='k', linestyle='--')
    fig.tight_layout()
    fig.savefig(name+'_UFF.pdf', dpi=720,
                bbox_inches='tight')
    plt.close()
    fig, ax = plotting.scatter_plot(X=dihedrals, Y=rel_GFN,
                                    ytitle='relative GFN2-xTB energy [kJ/mol]',
                                    xtitle='NLLN dihedral [degrees]',
                                    ylim=GFN_range,
                                    xlim=(-10, 200),
                                    c='#64B5F6', alpha=0.8,
                                    edgecolors='none')
    GFN_XRD_energy1 = 0
    GFN_XRD_energy2 = 0
    ax.axhline(y=GFN_XRD_energy1, c='k', linestyle='--')
    ax.axhline(y=GFN_XRD_energy2, c='k', linestyle='--')
    # do dihedral limits
    ax.axvline(x=20, c='k', linestyle='--')
    fig.tight_layout()
    fig.savefig(name+'_GFN.pdf', dpi=720,
                bbox_inches='tight')
    plt.close()


def get_clever_XRD_energies(FF):
    '''Return the energies (kJ/mol) of all ligands in the 3 clever cages.

    l == large ligand, s == small ligand

    '''
    energies = {}
    if FF == 'UFF':
        # all energies of ligands in each cage
        energies['ABCBA_300'] = [661.7335562384677, 629.6775797057525,
                                 1330.784565287804, 1325.1063252078732]
        energies['ABCBA_420'] = [1409.3375061168201, 1040.3635361898941,
                                 1169.4324281595798, 1130.3264249226545]
        energies['ABA_51'] = [487.49187504169936, 492.0550063290009,
                              1002.6791172969815, 995.3649163368942]
    return energies


def add_clever_geom_lines(ax, sum=False):
    '''Add horiz and vertical lines to axes at hardcoded places based on analysis of
    bloch2017 cages.

    '''
    if sum is False:
        # cage 1
        # # max deviation from planarity for all four N-Pd-N vectors
        # ax.axhline(y=1.232, c='b', label='cage 1 (GFN)', alpha=0.4, linestyle='-')
        # max deviation of NN vector differences of small molecule
        ax.axhline(y=1.232, c='b', label='cage 1 (GFN)', alpha=0.4, linestyle='-')
        # max angle difference from 180 for all four N-Pd-N vectors
        ax.axvline(x=6.3, c='b', alpha=0.4, linestyle='-')
        # cage 2
        # max deviation from planarity for all four N-Pd-N vectors
        ax.axhline(y=0.701, c='r', label='cage 2 (XRD)', alpha=0.4, linestyle='--')
        # max angle difference from 180 for all four N-Pd-N vectors
        ax.axvline(x=7.1, c='r', alpha=0.4, linestyle='--')
    else:
        # cage 1
        # # max deviation from planarity for all four N-Pd-N vectors
        # ax.axhline(y=1.232, c='b', label='cage 1 (GFN)', alpha=0.4, linestyle='-')
        # max of sum deviations of NN vector differences of small molecule
        ax.axhline(y=max([0.766+0.066, 0.810+0.240]), c='b',
                   label='cage 1 (GFN)', alpha=0.4, linestyle='-')
        # max of sum of angle differences from 180 of pairs of NN-NPd vectors
        ax.axvline(x=max([6.3+4.8, 4.3+4.9]), c='b', alpha=0.4, linestyle='-')
        # cage 2
        # max of sum deviations of NN vector differences of small molecule
        ax.axhline(y=max([0.2414+0.2280, 0.310+0.8500]), c='r',
                   label='cage 2 (XRD)', alpha=0.4, linestyle='--')
        # max of sum of angle differences from 180 of pairs of NN-NPd vectors
        ax.axvline(x=max([7.1+3, 4.7+4.5]), c='r', alpha=0.4, linestyle='--')


def get_all_pairs(molecule_pop, settings, mol_pair=None):
    '''Get all molecule pairs as ::class::Combination from molecule population.

    '''
    # define bond length vector to use based on N-Pd bond distances extracted
    # from survey
    # N-Pd-N length
    vector_length = settings['bond_mean']
    vector_std = settings['bond_std']
    # obtain all pair properties in molecule DB
    # poly1 should be the 'large' molecule, while poly2 should be the 'small'
    # molecule of the pair
    all_pairs = []
    for i, poly1 in enumerate(molecule_pop):
        logging.info(f'molecule: {poly1.name}')
        # turn on pair specific checks
        if mol_pair is not None:
            if poly1.name != mol_pair[0]:
                continue
        for j, poly2 in enumerate(molecule_pop):
            # make sure poly1 != poly2
            if i == j:
                continue
            # turn on pair specific checks
            if mol_pair is not None:
                if poly2.name != mol_pair[1]:
                    continue
            logging.info(f'pair: {poly1.name}, {poly2.name}')
            for conf1 in poly1.geom_prop:
                PROP1 = poly1.geom_prop[conf1]
                # skip conformer if dihedral meant the N's were not on the
                # right side or Ns are pointing the wrong way
                if PROP1['skip'] is True:
                    continue
                for conf2 in poly2.geom_prop:
                    PROP2 = poly2.geom_prop[conf2]
                    # skip conformer if dihedral meant the N's were not on the
                    # right side or Ns are pointing the wrong way
                    if PROP2['skip'] is True:
                        continue
                    # define pair ordering by the NN vector length
                    # mol == larger molecule, smol == smaller molecule.
                    if np.linalg.norm(np.asarray(PROP1['NN_v'])) >= np.linalg.norm(np.asarray(PROP2['NN_v'])):
                        comb = Combiner.Combination(lmol=poly1, smol=poly2,
                                                    lconf=conf1, sconf=conf2)
                        comb.popn_ids = (i, j)
                    else:
                        comb = Combiner.Combination(lmol=poly2, smol=poly1,
                                                    lconf=conf2, sconf=conf1)
                        comb.popn_ids = (j, i)
                    # if molecule1 or molecule2 energy > threshold from conf min
                    # skip pair
                    # if comb.lenergy > settings['energy_tol']:
                    #     continue
                    # if comb.senergy > settings['energy_tol']:
                    #     continue
                    # obtain all properties
                    # 16/05/19 -- not checking N-N distances
                    # check N-N distance of poly1-conf > poly2-conf
                    # only save combinations with lNN_dist > sNN_dist
                    # if mol_pair is not None, turn on pair specific checks
                    # we dont check for NN distances in this case, i.e.
                    # we DO check if mol_pair is None
                    # if mol_pair is None:
                    #     if comb.test_N_N_lengths() is False:
                    #         continue
                    # get final geometrical properties
                    # comb.calculate_planarity(vector_length=vector_length)
                    comb.get_ideal_length_deviation(vector_length=vector_length)
                    # check that the pairs sum to 180
                    comb.get_angle_deviations()
                    # comb.get_planarity_deviation()
                    all_pairs.append(comb)
    return all_pairs


def output_analysis(molecule_pop, pair_data, angle_tol, energy_tol,
                    mol_pair=None):
    '''Output the pair analysis for all pairs with all molecules or just the
    pair in mol_pair.

    '''
    for p, poly1 in enumerate(molecule_pop):
        combinations = [i for i in pair_data
                        if p == i.popn_ids[0]]
        if len(combinations) == 0:
            continue
        if mol_pair is None:
            prefix = poly1.name + '_analysis_'
        else:
            prefix = mol_pair[0]+'-'+mol_pair[1]+'_'
        logging.info(f'molecule: {poly1.name}')
        logging.info(f'no. pairs: {len(combinations)}')
        # debug print statements
        # for i in combinations:
        #     i.print_all_properties()
        #     input()
        X_data = [i.sum_angle_dev
                  for i in combinations]
        Y_data = [i.sum_length_dev
                  for i in combinations]
        Z_data = [i.max_pair_energy/energy_tol
                  for i in combinations]
        # define colour map based on energy tol
        # cmap = {'mid_point': energy_tol/2/energy_tol,
        #         'cmap': cm.RdBu,
        #         'ticks': [0, energy_tol/2/energy_tol, energy_tol/energy_tol],
        #         'labels': ['0', str(energy_tol/2), str(energy_tol)],
        #         'cmap_label': 'energy [kJ/mol]'}

        fig, ax = plt.subplots(figsize=(8, 5))
        # cmp = plotting.define_plot_cmap(fig, ax,
        #                                 mid_point=cmap['mid_point'],
        #                                 cmap=cmap['cmap'],
        #                                 ticks=cmap['ticks'],
        #                                 labels=cmap['labels'],
        #                                 cmap_label=cmap['cmap_label'])
        # ax.scatter(X_data, Y_data, c=cmp(Z_data),
        #            edgecolors='k',
        #            marker='o', alpha=0.4, s=80)
        ax.scatter(X_data, Y_data, c='#C70039',
                   edgecolors='none',
                   marker='o', alpha=0.4, s=40)
        # Set number of ticks for x-axis
        ax.tick_params(axis='both', which='major', labelsize=16)
        # ax.set_xlabel('maximum angle deviation [degrees]', fontsize=16)
        ax.set_xlabel('sum |angle deviation| [degrees]', fontsize=16)
        ax.set_ylabel('sum |N-N distance deviation| [$\mathrm{\AA}$]',
                      fontsize=16)
        ax.set_xlim(0, 180)
        ax.set_ylim(0, 20)  # round(max(Y_data))+1)
        # add constraint lines
        add_clever_geom_lines(ax, sum=True)
        if mol_pair is None:
            ax.set_title(poly1.name, fontsize=16)
        else:
            ax.set_title(prefix.replace('_', ' '), fontsize=16)
            ax.legend(fontsize=12)
        fig.tight_layout()
        fig.savefig(prefix+'main.pdf', dpi=360,
                    bbox_inches='tight')
        plt.close()


def plot_all_pair_info(pair_data, angle_tol, energy_tol):
    '''Do multi dimensional plot of all molecule pair information.

    '''
    markers = ['o', 'X', 'P', 'D', '>', '<', 's', '^', 'p', '*', 'h', 'v']
    fig, ax = plt.subplots(figsize=(8, 5))

    # define colour map based on energy tol
    cmap = plotting.define_plot_cmap(fig, ax,
                                     mid_point=energy_tol/2/energy_tol,
                                     cmap=cm.RdBu,
                                     ticks=[0, energy_tol/2/energy_tol, energy_tol/energy_tol],
                                     labels=['0', str(energy_tol/2), str(energy_tol)],
                                     cmap_label='energy [kJ/mol]')

    X_data = [max([i.angle1_deviation, i.angle2_deviation])
              for i in pair_data if i.test_N_N_lengths]
    Y_data = [i.NPdN_difference
              for i in pair_data if i.test_N_N_lengths]
    Z_data = [max([i.energy1, i.energy2])/energy_tol
              for i in pair_data if i.test_N_N_lengths]
    # M_data = [markers[i.popn_ids[0]]
    #           for i in pair_data if i.test_N_N_lengths]
    X_max = max(X_data)
    Y_max = max(Y_data)

    ax.scatter(X_data, Y_data, c=cmap(Z_data), edgecolors='k',
               marker='o', alpha=0.5, s=80)
    # ax.axhline(pair_data[0].tol, c='k', alpha=0.5)
    # ax.axvline(angle_tol, c='k', alpha=0.5)
    # Set number of ticks for x-axis
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.set_xlabel('maximum angle deviation [degrees]', fontsize=16)
    ax.set_ylabel('deviation from planarity', fontsize=16)
    ax.set_xlim(0, round(X_max+1))
    ax.set_ylim(0, round(Y_max+1))
    fig.tight_layout()
    fig.savefig('all_pair_info.pdf', dpi=720,
                bbox_inches='tight')
