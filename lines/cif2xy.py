#!/usr/bin/env python

#    Lines - a python plotting program
#    Copyright (C) 2015 Stef Smeets
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import subprocess as sp
import sys
import os
import argparse

import numpy as np

from xcore.formats import read_cif

__version__ = "2015-10-01"

planck_constant = 6.62606957E-34
elementary_charge = 1.60217656E-19
speed_of_light = 2.99792458E8


def energy2wavelength(E):
    """Takes wavelength in keV, returns energy in Angstrom"""
    # 1E3 from ev to kev, divide by 1E10 from angstrom to meter
    return 1E10*planck_constant*speed_of_light/(E*1E3*elementary_charge)


def replace_extension(fn, new=".xy"):
    """replaces cif extension by xy extension"""
    root, ext = os.path.splitext(fn)
    basename = os.path.basename(root)
    xy_out = basename + "." + new
    return xy_out


def cif2xy(cif, wl=1.0):
    print "Reading CIF:", cif

    cell, atoms = read_cif(cif)

    a, b, c, al, be, ga = cell.parameters

    spgr = cell.spgr_name

    title = 'lines'

    xy_out = replace_extension(cif, new="xy")

    focus_inp = open("focus.inp", 'w')
    focus_out = "focus.out"

    print >> focus_inp, """
Title  {title}

SpaceGroup  {spgr}
UnitCell  {a} {b} {c} {al} {be} {ga}

Lambda  {wl}

ProfileStartEndStep 2 49.99 0.002
ProfilePOLRA 1.0
ProfileFWHM UVW 0.001 0.0 0.0
#ProfileAsym  a(i) -0.005 0.003 0
ProfilePeakShape  PseudoVoigt
PseudoVoigtPeakRange  25
PseudoVoigtFracLorentz  0.5
ProfileBackground  0
#ProfileReferenceRefl
ProfileReferenceMax  50000

""".format(title=title,
           spgr=spgr,
           a=a,
           b=b,
           c=c,
           al=al,
           be=be,
           ga=ga,
           wl=wl)

    for i, atom in atoms.iterrows():
        label = atom.label
        element = atom.symbol
        if element == 'T':
            element = 'Si'
        x, y, z = atom.x, atom.y, atom.z
        occ = atom.occ
        u_iso = atom.biso / (8*np.pi**2)

        print >> focus_inp, '{label:8} {element:4} {x:8.5f} {y:8.5f} {z:8.5f} {occ:.4f} {u_iso:.4f}'.format(label=label,
                                                                                                            element=element,
                                                                                                            x=x, y=y, z=z,
                                                                                                            occ=occ,
                                                                                                            u_iso=u_iso)
    print >> focus_inp, "End"
    focus_inp.close()

    print "Generating powder pattern... (wl = {} A)".format(wl)
    sp.call(
        "focus -PowderStepScan {} > {}".format(focus_inp.name, focus_out), shell=True)

    begin_switch = ">Begin stepscan"
    end_switch = "&"

    focus_stepscan = open(focus_out, 'r')
    xye = open(xy_out, 'w')

    do_print = 0
    for line in focus_stepscan:
        if line.startswith(end_switch):
            break
        elif do_print:
            print >> xye, line,
        elif line.startswith(begin_switch):
            do_print = 1
            focus_stepscan.next()
    focus_stepscan.close()
    xye.close()

    return xy_out


def main():
    description = """"""
    
    epilog = 'Updated: {}'.format(__version__)

    parser = argparse.ArgumentParser(description=description,
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     version=__version__)

    def parse_wl(string):
        wavelengths = {"cra1": 2.28970, "cra2": 2.29361, "cr": 2.2909,
                       "fea1": 1.93604, "fea2": 1.93998, "fe": 1.9373,
                       "cua1": 1.54056, "cua2": 1.54439, "cu": 1.5418,
                       "moa1": 0.70930, "moa2": 0.71359, "mo": 0.7107,
                       "aga1": 0.55941, "aga2": 0.56380, "ag": 0.5608, "sls": 1.0000}
        if string.lower().endswith('kev'):
            return energy2wavelength(float(string.lower().replace('kev', "")))
        elif string.lower() in wavelengths:
            return wavelengths[string.lower()]
        else:
            return float(string)

    parser = argparse.ArgumentParser()

    parser.add_argument("args",
                        type=str, metavar="FILE", nargs='*',
                        help="Paths to cif files.")

    parser.add_argument("--wavelength",
                        action="store", type=parse_wl, dest='wavelength',
                        help="Specify the wavelength to use for the powder pattern generation. Default = 1.0 Angstrom")

    parser.set_defaults(wavelength=1.0)

    options = parser.parse_args()
    args = options.args

    for arg in args:
        out = cif2xy(arg, wl=options.wavelength)
        print "Printed powder pattern to", out
        print

if __name__ == '__main__':
    main()
