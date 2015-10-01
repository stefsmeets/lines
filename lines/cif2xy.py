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

try:
	from cctbx import xray
	from cctbx import crystal
	from iotbx.cif import reader, CifParserError
except ImportError:
	CCTBX_LOADED = False
else:
	CCTBX_LOADED = True

__version__ = "2015-10-01"

if not CCTBX_LOADED:
	import environment

	platform = sys.platform

	if platform =="darwin":
		environment.set_environment_variables_osx()
		sp.call([sys.executable, os.path.abspath(__file__)] + sys.argv[1:]) # call self
	elif platform =="win32":
		environment.set_environment_variables_windows()
		sp.call([sys.executable, os.path.abspath(__file__)] + sys.argv[1:]) # call self
	elif platform =="linux2":
		environment.set_environment_variables_linux()
		sp.call([sys.executable, os.path.abspath(__file__)] + sys.argv[1:]) # call self
	else:
		print "Operating system not supported!"
		exit()
	exit()

def read_cif(f):
	"""opens cif and returns cctbx data object"""
	try:
		if isinstance(f,file):
			structures = reader(file_object=f).build_crystal_structures()
		elif isinstance(f,str):
			structures = reader(file_path=f).build_crystal_structures()
		else:
			raise TypeError, 'read_cif: Can not deal with type {}'.format(type(f))
	except CifParserError as e:
		print e
		print "Error parsing cif file, check if the data tag does not contain any spaces."
		exit()
	for key,val in structures.items():
		print "\nstructure:", key
		val.show_summary()
		print "Volume: {:.2f}".format(val.unit_cell().volume())
		print
	return structures


def replace_extension(fn, new=".xy"):
	"""replaces cif extension by xy extension"""
	root,ext = os.path.splitext(fn)
	basename = os.path.basename(root)
	xy_out = basename + "." + new
	return xy_out


def cif2xy(cif, wl=1.0):
	print "Reading CIF:", cif

	structure = read_cif(cif).values()[0]
	sg = structure.space_group()
	uc = structure.unit_cell()
	sps = structure.special_position_settings()
	scatterers = structure.scatterers()

	title = 'lines'
	spgr = sg.type().lookup_symbol()
	a,b,c,al,be,ga = uc.parameters()

	xy_out = replace_extension(cif, new="xy")

	focus_inp = open("focus.inp",'w')
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

	for atom in scatterers:
		label = atom.label
		element = atom.element_symbol()
		if element == 'T':
			element = 'Si'
		x,y,z = atom.site
		occ = atom.occupancy
		u_iso = atom.u_iso

		print >> focus_inp, '{label:8} {element:4} {x:8.5f} {y:8.5f} {z:8.5f} {occ:.4f} {u_iso:.4f}'.format(label=label,
																	element=element,
																	x=x,y=y,z=z,
																	occ=occ,
																	u_iso=u_iso)
	print >> focus_inp, "End"
	focus_inp.close()

	print "Generating powder pattern... (wl = {} A)".format(wl)
	sp.call("focus -PowderStepScan {} > {}".format(focus_inp.name, focus_out), shell=True)

	begin_switch = ">Begin stepscan"
	end_switch = "&"

	focus_stepscan = open(focus_out,'r')
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
	usage = """"""

	description = """Notes:
- Requires CCTBX
"""	
	
	epilog = 'Updated: {}'.format(__version__)
	
	parser = argparse.ArgumentParser(#usage=usage,
									description=description,
									epilog=epilog, 
									formatter_class=argparse.RawDescriptionHelpFormatter,
									version=__version__)

	def parse_wl(string):
		wavelengths = { "cra1" : 2.28970 ,  "cra2" : 2.29361 ,  "cr" : 2.2909 ,
                        "fea1" : 1.93604 ,  "fea2" : 1.93998 ,  "fe" : 1.9373 ,
                        "cua1" : 1.54056 ,  "cua2" : 1.54439 ,  "cu" : 1.5418 ,
                        "moa1" : 0.70930 ,  "moa2" : 0.71359 ,  "mo" : 0.7107 ,
                        "aga1" : 0.55941 ,  "aga2" : 0.56380 ,  "ag" : 0.5608 , "sls": 1.0000 }
		if string.lower().endswith('kev'):
			return energy2wavelength(float(string.lower().replace('kev',"")))
		elif string.lower() in wavelengths:
			return wavelengths[string.lower()]
		else:
			return float(string)

	parser = argparse.ArgumentParser()

	parser.add_argument("args", 
						type=str, metavar="FILE",nargs='*',
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