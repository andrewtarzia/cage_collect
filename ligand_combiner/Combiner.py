#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Distributed under the terms of the MIT License.

"""
Module for containing functions for ligand_combiner

Author: Andrew Tarzia

Date Created: 17 Apr 2019

"""

import sys
import logging
import ase
import numpy as np
from rdkit.Chem import AllChem as Chem
import os
import stk
sys.path.insert(0, '/home/atarzia/thesource/')
import stk_f
import calculations


class Combination:
    '''Class defining a pair of linkers and their geometrical properties

    '''
    def __init__(self, lmol, smol, lconf, sconf):
        '''Obtains all properties provided as attributes of lmol/smol.

        '''
        self.lmol = lmol
        self.smol = smol
        self.lconf = lconf
        self.sconf = sconf
        # get relative UFF energy from two molecule objects
        self.lenergy = lmol.geom_prop[lconf]['rel_energy']
        self.senergy = smol.geom_prop[sconf]['rel_energy']
        self.max_pair_energy = max([self.lenergy, self.senergy])
        # get NN distances
        self.lNN_dist = np.linalg.norm(lmol.geom_prop[lconf]['NN_v'])
        self.sNN_dist = np.linalg.norm(smol.geom_prop[sconf]['NN_v'])
        # get all trapezoid angles
        self.l_angle1 = lmol.geom_prop[lconf]['NN_BCN_1']
        self.l_angle2 = lmol.geom_prop[lconf]['NN_BCN_2']
        self.s_angle1 = smol.geom_prop[sconf]['NN_BCN_1']
        self.s_angle2 = smol.geom_prop[sconf]['NN_BCN_2']

    def calculate_planarity(self, vector_length):
        '''Calculate the planarity between binding atoms of the pair of molecules.

        Definition:

        # now check that the length of the long
        # vector and the short vector are commensurate
        # with an ideal trapezoid with the given angles
        # i.e. the extender vector determined by the
        # difference of the two NN_v (LHS) matches what is
        # expected by trig (RHS)

        '''
        print('You need to write the definition into the DOCS')
        # LHS1 == LHS2 as defined by length of NN vectors, which are the same
        self.LHS1 = (self.lNN_dist - self.sNN_dist) / 2
        self.LHS2 = (self.lNN_dist - self.sNN_dist) / 2
        self.souter_angle1 = np.radians(180 - self.s_angle1)
        self.souter_angle2 = np.radians(180 - self.s_angle2)
        # RHS = 2|C| * cos(pi - angle)
        print(self.s_angle1)
        print((180 - self.s_angle1))
        print(np.radians(180 - self.s_angle1))
        print(self.souter_angle1)
        print(np.cos(self.souter_angle1))
        sys.exit()
        self.RHS1 = (2 * vector_length) * np.cos(self.souter_angle1)
        self.RHS2 = (2 * vector_length) * np.cos(self.souter_angle2)

    def calculate_ideal_small_NN(self, vector_length):
        '''Calculate the ideal NN distance of the small molecule based on large
        molecule and ideal trapezoid

        '''
        # because the binding vector angles are not actually the same we define
        # the ideal small NN based on both possible binding vector angles
        # i.e. two different ideal trapezoids
        bonding_vector_length = 2 * vector_length
        # print('vector lengths:', vector_length, bonding_vector_length)
        extension_1 = bonding_vector_length * np.cos(np.radians(self.l_angle1))
        extension_2 = bonding_vector_length * np.cos(np.radians(self.l_angle2))
        # print('extensions:', extension_1, extension_2)
        ideal_NN1 = self.lNN_dist - 2 * extension_1
        ideal_NN2 = self.lNN_dist - 2 * extension_2
        # print('ideal NNs:', ideal_NN1, ideal_NN2)
        return [ideal_NN1, ideal_NN2]

    def get_angle_deviations(self):
        '''Get the closeness of test angles to 180 degrees. As a sum and max of
        the two ends of the molecules.

        '''
        self.angle1_deviation = abs(180 - (self.l_angle1 + self.s_angle1))
        self.angle2_deviation = abs(180 - (self.l_angle2 + self.s_angle2))
        self.max_angle_dev = max([self.angle1_deviation, self.angle2_deviation])
        self.sum_angle_dev = sum([self.angle1_deviation, self.angle2_deviation])

    def get_planarity_deviation(self):
        '''Get the difference of the LHS and RHS that are defined by the
        N-Pd-N distance

        '''
        self.planar_dev1 = abs(self.LHS1-self.RHS1)
        self.planar_dev2 = abs(self.LHS2-self.RHS2)
        self.max_planar_dev = max([self.planar_dev1, self.planar_dev2])

    def get_ideal_length_deviation(self, vector_length):
        '''Get the max and sum of the differences between the actual N-N distance
        of the small molecule and the idealized distances from trapezoid.

        '''
        ideal_NNs = self.calculate_ideal_small_NN(vector_length=vector_length)
        self.sum_length_dev = sum([abs(self.sNN_dist - i) for i in ideal_NNs])
        self.max_length_dev = max([abs(self.sNN_dist - i) for i in ideal_NNs])

    def test_N_N_lengths(self):
        '''Test that the larger linker has a longer NN distance than the shorter
        linker.

        '''
        if self.lNN_dist > self.sNN_dist:
            return True
        else:
            return False

    def print_all_properties(self):
        '''Print all properties of a Combination.

        '''
        print('mol names:', self.lmol.name, self.smol.name)
        print('conformers:', self.lconf, self.sconf)
        print('energies:', self.lenergy, self.senergy)
        print('NN distances:', self.lNN_dist, self.sNN_dist)
        # print('LHSs:', self.LHS1, self.LHS2)
        print('l angles:', self.l_angle1, self.l_angle2)
        print('s angles:', self.s_angle1, self.s_angle2)
        # print('s outer angles:', self.souter_angle1, self.souter_angle2)
        # print('RHSs:', self.RHS1, self.RHS2)
        print('angle devs:', self.angle1_deviation, self.angle2_deviation)
        # print('planarity devs:', self.planar_dev1, self.planar_dev2)
        print('------------------------------------------------')
        print('max angle dev', self.max_angle_dev)
        print('sum angle dev', self.sum_angle_dev)
        print('max length dev', self.max_length_dev)
        print('sum length dev', self.sum_length_dev)


def atoms_2_vect(ASE, p1, p2):
    '''Append to ASE.Atoms() the interpolation between two points.

    '''
    pts = [np.linspace(p1[i], p2[i]) for i in np.arange(len(p1))]
    for i, j, k in zip(*pts):
        ASE.append(ase.Atom(symbol='P', position=[i, j, k]))
    return ASE


def visualize_atoms(mol, conf_dict, cid, type, filename):
    '''Output files with POIs and conformer atom positions for visulization.

    '''

    mol.write(path=filename + '.pdb', conformer=cid)
    POIs = ase.Atoms()
    POIs.append(ase.Atom(symbol='H', position=conf_dict['COM']))
    POIs.append(ase.Atom(symbol='C', position=conf_dict['liga1']['pos']))
    POIs.append(ase.Atom(symbol='C', position=conf_dict['core1']['pos']))
    POIs.append(ase.Atom(symbol='C', position=conf_dict['liga2']['pos']))
    POIs.append(ase.Atom(symbol='Be', position=conf_dict['liga1']['CC_pos']))
    POIs.append(ase.Atom(symbol='Be', position=conf_dict['liga2']['CC_pos']))
    POIs.append(ase.Atom(symbol='O', position=conf_dict['liga1']['N_pos']))
    POIs.append(ase.Atom(symbol='O', position=conf_dict['liga2']['N_pos']))
    # plot vectors as P atom
    POIs = atoms_2_vect(ASE=POIs, p1=conf_dict['liga1']['CC_pos'],
                        p2=conf_dict['liga1']['N_pos'])
    POIs = atoms_2_vect(ASE=POIs, p1=conf_dict['liga2']['CC_pos'],
                        p2=conf_dict['liga2']['N_pos'])
    POIs = atoms_2_vect(ASE=POIs, p1=conf_dict['liga1']['N_pos'],
                        p2=conf_dict['liga2']['N_pos'])
    # if type == 'ABCBA':
    #    POIs.append(Atom(symbol='C', position=conf_dict['link1']['pos']))
    #    POIs.append(Atom(symbol='C', position=conf_dict['link2']['pos']))
    POIs.write(filename + '_POIs.xyz')


def get_binding_N_CC_coord(molecule, conf, frag_id):
    '''Get the midpoint of the vector connecting the single (assumption)
    binding N in ligand building block using the building_block_cores of
    molecule.

    '''
    # assumes that the ligand block is always building block index '0'
    # get coord of possible Ns
    for i, frag in enumerate(molecule.building_block_cores(0)):
        if i == frag_id:
            frag_c = frag.GetConformer(conf)
            for atom in frag.GetAtoms():
                atom_id = atom.GetIdx()
                atom_position = frag_c.GetAtomPosition(atom_id)
                atom_position = np.array([*atom_position])
                type = frag.GetAtomWithIdx(atom_id).GetSymbol()
                if type == 'N':
                    # get neighbours of this N
                    C_ids = []
                    for atom2 in atom.GetNeighbors():
                        atom2_id = atom2.GetIdx()
                        # if they are carbons
                        if frag.GetAtomWithIdx(atom2_id).GetSymbol():
                            C_ids.append(atom2_id)
                    CC1_id = C_ids[0]
                    CC2_id = C_ids[1]
                    # get their atom positions
                    CC1_pos = frag_c.GetAtomPosition(CC1_id)
                    CC1 = np.array([*CC1_pos])
                    CC2_pos = frag_c.GetAtomPosition(CC2_id)
                    CC2 = np.array([*CC2_pos])
                    # get the vector between C neighbours
                    CC_v = CC1 - CC2
                    # get the midpoint of the vector
                    CC_midpoint = CC1 - CC_v / 2
                    return CC_midpoint


def get_binding_N_coord(molecule, conf, frag_id):
    '''Get the single (assumption) binding N in ligand building block using the
    building_block_cores of molecule.

    '''
    # assumes that the ligand block is always building block index '0'
    # get coord of possible Ns
    for i, frag in enumerate(molecule.building_block_cores(0)):
        if i == frag_id:
            frag_c = frag.GetConformer(conf)
            for atom in frag.GetAtoms():
                atom_id = atom.GetIdx()
                atom_position = frag_c.GetAtomPosition(atom_id)
                atom_position = np.array([*atom_position])
                type = frag.GetAtomWithIdx(atom_id).GetSymbol()
                if type == 'N':
                    return atom_position


def bb_center_of_mass(molecule, conf, bb_idx, frag_id):
    '''Get the center_of_mass of the core of the building block with bb_idx
    and frag_id post building.

    '''
    for i, frag in enumerate(molecule.building_block_cores(bb_idx)):
        if i == frag_id:
            center = np.array([0., 0., 0.])
            total_mass = 0.
            frag_c = frag.GetConformer(conf)
            if frag.GetAtoms():
                for atom in frag.GetAtoms():
                    atom_id = atom.GetIdx()
                    atom_position = frag_c.GetAtomPosition(atom_id)
                    atom_position = np.array([*atom_position])
                    mass = frag.GetAtomWithIdx(atom_id).GetMass()
                    total_mass += mass
                    center += mass * atom_position
                return np.divide(center, total_mass)
            else:
                return np.array([0., 0., 0.])
    return np.array([0., 0., 0.])


def check_binder_directions(mol, cid):
    '''Check that binding vectors facing away from core molecule.

    # also check that the N atoms are pointing away from the core
    # by making sure COM_core-N_pos > COM_core-liga_pos
    '''
    core_2_COM = np.asarray(mol.geom_prop[cid]['COM']) \
        - np.asarray(mol.geom_prop[cid]['core1']['pos'])
    core_2_N1 = np.asarray(mol.geom_prop[cid]['liga1']['N_pos']) \
        - np.asarray(mol.geom_prop[cid]['core1']['pos'])
    core_2_liga1 = np.asarray(mol.geom_prop[cid]['liga1']['pos']) \
        - np.asarray(mol.geom_prop[cid]['core1']['pos'])
    core_2_N2 = np.asarray(mol.geom_prop[cid]['liga2']['N_pos']) \
        - np.asarray(mol.geom_prop[cid]['core1']['pos'])
    core_2_liga2 = np.asarray(mol.geom_prop[cid]['liga2']['pos']) \
        - np.asarray(mol.geom_prop[cid]['core1']['pos'])

    N1_core_COM_angle = calculations.angle_between(core_2_N1, core_2_COM)
    L1_core_COM_angle = calculations.angle_between(core_2_liga1, core_2_COM)
    N2_core_COM_angle = calculations.angle_between(core_2_N2, core_2_COM)
    L2_core_COM_angle = calculations.angle_between(core_2_liga2, core_2_COM)

    if N1_core_COM_angle > L1_core_COM_angle:
        if N2_core_COM_angle > L2_core_COM_angle:
            return True
    return False


def get_geometrical_properties(mol, cids, type):
    '''Calculate the geometrical properties of all conformers

    '''
    # minimum energy of all conformers
    energies = []
    for cid in cids:
        energies.append(get_energy(stk_mol=mol, conformer=cid, FF='UFF'))
    min_E = min(energies)

    # new attribute for mol
    mol.geom_prop = {}
    passed = 0
    total = 0
    for cid in cids:
        total += 1
        # dictinary per conformer
        conf_dict = {}
        # get energy relative to minimum for all conformers
        conf_dict['energy'] = get_energy(stk_mol=mol, conformer=cid, FF='UFF')
        conf_dict['rel_energy'] = conf_dict['energy'] - min_E
        # get molecule COM
        conf_dict['COM'] = mol.center_of_mass(conformer=cid).tolist()
        if type == 'ABCBA':
            # first binder -- actual ordering of BB does not matter if linker
            # information is not used
            conf_dict['liga1'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=0, frag_id=0).tolist(),
                'N_pos': get_binding_N_coord(molecule=mol, conf=cid,
                                             frag_id=0).tolist(),
                'CC_pos': get_binding_N_CC_coord(molecule=mol, conf=cid,
                                                 frag_id=0).tolist()}
            # second binder -- actual ordering of BB does not matter if linker
            # information is not used
            conf_dict['liga2'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=0, frag_id=1).tolist(),
                'N_pos': get_binding_N_coord(molecule=mol, conf=cid,
                                             frag_id=1).tolist(),
                'CC_pos': get_binding_N_CC_coord(molecule=mol, conf=cid,
                                                 frag_id=1).tolist()}
            # first linker -- actual ordering of BB does matter if linker
            # information is used -- currently is not
            conf_dict['link1'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=1, frag_id=0).tolist()}
            # second linker -- actual ordering of BB does matter if linker
            # information is used -- currently is not
            conf_dict['link2'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=1, frag_id=1).tolist()}
            # core
            conf_dict['core1'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=2, frag_id=0).tolist()}
        elif type == 'ABA':
            # first binder -- actual ordering of BB does not matter
            conf_dict['liga1'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=0, frag_id=0).tolist(),
                'N_pos': get_binding_N_coord(molecule=mol, conf=cid,
                                             frag_id=0).tolist(),
                'CC_pos': get_binding_N_CC_coord(molecule=mol, conf=cid,
                                                 frag_id=0).tolist()}
            # second binder -- actual ordering of BB does not matter
            conf_dict['liga2'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=0, frag_id=1).tolist(),
                'N_pos': get_binding_N_coord(molecule=mol, conf=cid,
                                             frag_id=1).tolist(),
                'CC_pos': get_binding_N_CC_coord(molecule=mol, conf=cid,
                                                 frag_id=1).tolist()}
            # core
            conf_dict['core1'] = {
                'pos': bb_center_of_mass(molecule=mol, conf=cid,
                                         bb_idx=1, frag_id=0).tolist()}
        mol.geom_prop[cid] = conf_dict
        # from the positions collected:
        # determine whether the N's are both pointing in the desired direction
        # if so,
        # determine N-N vector -> NN_v
        # determine binder core - N vectors -> BCN_1, BCN_2
        # determine binder core - binder core vector -> BCBC_v
        # calculate the angle between:
        # -- BCBC_v and BCN_i
        # -- NN_v and BCN_i (make sure the origin is not important)

        # to determine if the N's are point the right way:
        # calculate the dihedral between N1 - liga1_com - liga2_com - N2
        NBBN_dihedral = calculations.get_dihedral(pt1=mol.geom_prop[cid]['liga1']['N_pos'],
                                                  pt2=mol.geom_prop[cid]['liga1']['pos'],
                                                  pt3=mol.geom_prop[cid]['liga2']['pos'],
                                                  pt4=mol.geom_prop[cid]['liga2']['N_pos'])
        # if the absolute value of this dihedral > some tolerance,
        # skip conformer
        mol.geom_prop[cid]['skip'] = False
        dihedral_lim = 20
        if abs(NBBN_dihedral) > dihedral_lim:
            mol.geom_prop[cid]['skip'] = True
            # logging.info(f'{mol.name}: confomer {cid} SKIPPPED - NBBN dihed = {NBBN_dihedral}')
            continue

        # also check that the N atoms are pointing away from the core
        # by making sure COM_core-N_pos > COM_core-liga_pos
        if check_binder_directions(mol=mol, cid=cid):
            mol.geom_prop[cid]['skip'] = True
            # logging.info(f'{mol.name}: confomer {cid} SKIPPPED - N backwards')
            continue

        NN_v = np.asarray(mol.geom_prop[cid]['liga1']['N_pos']) \
            - np.asarray(mol.geom_prop[cid]['liga2']['N_pos'])
        BCN_1 = np.asarray(mol.geom_prop[cid]['liga1']['CC_pos']) \
            - np.asarray(mol.geom_prop[cid]['liga1']['N_pos']).tolist()
        BCN_2 = np.asarray(mol.geom_prop[cid]['liga2']['CC_pos']) \
            - np.asarray(mol.geom_prop[cid]['liga2']['N_pos']).tolist()
        mol.geom_prop[cid]['NN_v'] = NN_v.tolist()
        mol.geom_prop[cid]['BCN_1'] = BCN_1.tolist()
        mol.geom_prop[cid]['BCN_2'] = BCN_2.tolist()
        passed += 1
        # output for viz
        # if False:
        if True:
            visualize_atoms(mol, conf_dict, cid, type,
                            filename=mol.name + '_' + str(cid))

        # get desired angles in radian
        # negative signs applied based on the direction of vectors defined
        # above - not dependance on ordering of BB placement in stk
        mol.geom_prop[cid]['NN_BCN_1'] = float(
            np.degrees(
                calculations.angle_between(
                    np.asarray(mol.geom_prop[cid]['BCN_1']),
                    np.asarray(mol.geom_prop[cid]['NN_v']))))
        mol.geom_prop[cid]['NN_BCN_2'] = float(
            np.degrees(
                calculations.angle_between(
                    np.asarray(mol.geom_prop[cid]['BCN_2']),
                    -np.asarray(mol.geom_prop[cid]['NN_v']))))
        # logging.info(f'{mol.name}: confomer {cid} passed')

    logging.info(f'{passed} of {total} passed, {round(passed/total, 2)*100} %')

    return mol


def get_energy(stk_mol, conformer, FF):
    '''Get MMFF energy using rdkit of a conformer of stk_mol.

    '''
    if FF == 'UFF':
        from stk import UFFEnergy
        ff = UFFEnergy()
    elif FF == 'MMFF':
        from stk import MMFFEnergy
        ff = MMFFEnergy()
    # Needs to be sanitized to get force field params.
    Chem.SanitizeMol(stk_mol.mol)
    energy = ff.energy(stk_mol, conformer=conformer)
    return energy*4.184  # kcal/mol to kJ/mol


def minimize_all_conformers(stk_mol, confs, FF):
    '''Energy minimize all conformers in stk.Molecule() using MMFF in rdkit

    '''
    for cid in confs:
        if FF == 'UFF':
            from stk import UFF
            uff = UFF()
            uff.optimize(stk_mol, conformer=cid)
        elif FF == 'MMFF':
            from stk import MMFF
            mmff = MMFF()
            mmff.optimize(stk_mol, conformer=cid)


def get_molecule(type, popns, pop_ids, inverted, N=1, mole_dir='./'):
    '''Get N conformers of a coordination cage ligand molecule using
    stk polymer function. Molecule undergoes RDKIT ETKDG conformer search and
    optimization with MMFF.

    Keyword Arguments:
        type (str) - type of ligand, ABCBA or ABA
        popns (list of stk.Populations) - core, ligand and linker
            stk.Populations
        pop_ids (tuple of int) - population indices to use from core, ligand and
            linker populations
        N (int) - number of conformers to build
        mole_dir (str) - directory to save molecule to

    Returns:
        cids (list) - list of conformer IDs
        molecule (stk.Polymer) - polymer molecule with N conformers
            in molecule.mol

    '''
    core_item = popns[0][pop_ids[0]]
    liga_item = popns[1][pop_ids[1]]
    link_item = popns[2][pop_ids[2]]
    if type == 'ABCBA':
        molecule = stk_f.build_ABCBA(core=core_item,
                                     liga=liga_item,
                                     link=link_item,
                                     flippedlink=inverted)
        prefix = core_item.name + '_'
        prefix += liga_item.name + '_'
        if inverted:
            prefix += link_item.name + 'i'
        else:
            prefix += link_item.name
    elif type == 'ABA':
        molecule = stk_f.build_ABA(core=core_item,
                                   liga=liga_item)
        prefix = core_item.name + '_'
        prefix += liga_item.name

    # output as built
    json_file = prefix + '_' + type + '.json'
    molecule.dump(os.path.join(mole_dir, json_file))
    mol_file = prefix + '_' + type + '.mol'
    molecule.write(os.path.join(mole_dir, mol_file))
    # clean molecule with ETKDG
    embedder = stk.RDKitEmbedder(Chem.ETKDG())
    embedder.optimize(molecule)
    # output energy minimized
    json_file = prefix + '_' + type + '_opt.json'
    molecule.dump(os.path.join(mole_dir, json_file))
    mol_file = prefix + '_' + type + '_opt.mol'
    molecule.write(os.path.join(mole_dir, mol_file))
    # make N conformers of the polymer molecule
    etkdg = Chem.ETKDG()
    etkdg.randomSeed = 1000
    cids = Chem.EmbedMultipleConfs(mol=molecule.mol, numConfs=N,
                                   params=etkdg)
    # FF minimize all conformers
    # minimize_all_conformers(stk_mol=molecule, confs=cids, FF='UFF')
    # output each conformer to 3D structure if desired
    # for cid in cids:
    #     print(cid)
    #     print(Chem.MolToSmiles(molecule.mol))
    #     sys.exit()
    #     mol_file = prefix + '_' + type + '_' + str(cid) + '_opt.mol'
    #     molecule.write(path=join(mole_dir, mol_file), conformer=cid)
    return cids, molecule
