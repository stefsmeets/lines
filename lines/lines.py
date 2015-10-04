#!/usr/bin/env python2.7

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

import sys
import os
import argparse

from shutil import copyfile

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

from scipy.interpolate import interp1d

import math

# try:
# 	from IPython.terminal.embed import InteractiveShellEmbed
# 	InteractiveShellEmbed.confirm_exit = False
# 	ipshell = InteractiveShellEmbed(banner1='')
# except ImportError:
# 	pass

__version__ = '2015-10-03'

params = {'legend.fontsize': 10,
		  'legend.labelspacing': 0.1}
plt.rcParams.update(params)

LINESDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

planck_constant   = 6.62606957E-34
elementary_charge = 1.60217656E-19
speed_of_light    = 2.99792458E8

# print plt.get_backend()

iza_codes = ( 'ABW', 'ACO', 'AEI', 'AEL', 'AEN', 'AET', 'AFG', 'AFI', 'AFN', 'AFO', 'AFR', 'AFS',
'AFT', 'AFX', 'AFY', 'AHT', 'ANA', 'APC', 'APD', 'AST', 'ASV', 'ATN', 'ATO', 'ATS', 'ATT', 'ATV', 'AWO', 'AWW', 'BCT', 'BEA', 'BEC', 'BIK', 'BOF',
'BOG', 'BPH', 'BRE', 'BSV', 'CAN', 'CAS', 'CDO', 'CFI', 'CGF', 'CGS', 'CHA', 'CHI', 'CLO', 'CON', 'CZP', 'DAC', 'DDR', 'DFO', 'DFT', 'DOH', 'DON',
'EAB', 'EDI', 'EMT', 'EON', 'EPI', 'ERI', 'ESV', 'ETR', 'EUO', 'EZT', 'FAR', 'FAU', 'FER', 'FRA', 'GIS', 'GIU', 'GME', 'GON', 'GOO', 'HEU', 'IFR',
'IHW', 'IMF', 'IRR', 'ISV', 'ITE', 'ITH', 'ITR', 'ITV', 'ITW', 'IWR', 'IWS', 'IWV', 'IWW', 'JBW', 'JRY', 'JST', 'KFI', 'LAU', 'LEV', 'LIO', 'LIT',
'LOS', 'LOV', 'LTA', 'LTF', 'LTJ', 'LTL', 'LTN', 'MAR', 'MAZ', 'MEI', 'MEL', 'MEP', 'MER', 'MFI', 'MFS', 'MON', 'MOR', 'MOZ', 'MRE', 'MSE', 'MSO',
'MTF', 'MTN', 'MTT', 'MTW', 'MVY', 'MWW', 'NAB', 'NAT', 'NES', 'NON', 'NPO', 'NPT', 'NSI', 'OBW', 'OFF', 'OSI', 'OSO', 'OWE', 'PAR', 'PAU', 'PHI',
'PON', 'PUN', 'RHO', 'RON', 'RRO', 'RSN', 'RTE', 'RTH', 'RUT', 'RWR', 'RWY', 'SAF', 'SAO', 'SAS', 'SAT', 'SAV', 'SBE', 'SBN', 'SBS', 'SBT', 'SFE',
'SFF', 'SFG', 'SFH', 'SFN', 'SFO', 'SFS', 'SFV', 'SGT', 'SIV', 'SOD', 'SOF', 'SOS', 'SSF', 'SSY', 'STF', 'STI', 'STO', 'STT', 'STW', 'SVR', 'SZR',
'TER', 'THO', 'TOL', 'TON', 'TSC', 'TUN', 'UEI', 'UFI', 'UOS', 'UOZ', 'USI', 'UTL', 'UWY', 'VET', 'VFI', 'VNI', 'VSV', 'WEI', 'WEN', 'YUG', 'ZON' ,
'POS', 'JNT', 'IFW', 'UOV', 'CSV', 'EWT', 'PSI', 'IFY', 'ITN', 'SSO', 'IRN', 'IFO') # updated aug 2015


def lineno():
	"""Returns the current line number in our program."""
	import inspect
	return inspect.currentframe().f_back.f_lineno

def printer(data):
	"""Print things to stdout on one line dynamically"""
	sys.stdout.write("\r\x1b[K"+data.__str__())
	sys.stdout.flush()

def gen_read_files(paths):
	"""opens file, returns file object for reading"""
	for path in paths:
		try:
			f = open(path,'r')
		except IOError,e:
			print e
			#print 'Cannot open {} (IOError)'.format(path,e)
			exit(0)
		yield f

def read_file(path):
	"""opens file, returns file object for reading"""
	try:
		f = open(path,'r')
	except IOError,e:
		print e
		#print 'Cannot open {} (IOError)'.format(path,e)
		exit(0)
	return f


def read_data(fn,usecols=None,append_zeros=False,savenpy=False,suffix='',is_ticks=False,wl=1.0):
	if fn == 'stepco.inp':
		f = read_file(fn)
		return parse_xrs(f,return_as='d')

	root,ext = os.path.splitext(fn)

	if ext == '' and root.upper() in iza_codes:
		fn = parse_iza_code(code=root)
		return read_data(fn, wl=wl)

	if ext == '.cif':
		fn = run_cif2xy(fn, wl=wl)  # requires CCTBX and FOCUS
		return read_data(fn)

	if ext.lower() == '.xrdml':
		return parse_xrdml(fn)
	
	try:
		#raise IOError
		inp = np.load(root+'.npy')
	except (IOError, AssertionError):
		inp = np.loadtxt(fn,usecols=usecols,ndmin=2)
	else:
		ext = '.npy'
		fn = root+'.npy'

	if append_zeros:
		(i,j) = inp.shape
		inp = np.hstack((inp,np.zeros((i,1))))

	if inp.shape[1] > 3:
		print 'More than 3 columns read from {}, assuming x,y,esd, ignoring the rest.'.format(f.name)

	d = Data(inp, name=fn+suffix, is_ticks=is_ticks)

	if savenpy and ext != '.npy':
		np.save(root,inp)

	return d

def load_tick_marks(path,col=3):
	"""Checks if file exists and loads tick mark data as data class. Use column=3 default for xrs"""
	try:
		f = open(path,'r')
		f.close()
	except IOError:
		print '-- {} not found. (IOError)'.format(path)
		return None

	ticks = read_data(path,usecols=(col,),append_zeros=True,is_ticks=True)
	return ticks

def get_correlation_matrix(f,topas=False):
	names = []
	lst_not_iprm = []
	def yield_corrmat(f):
		for i,line in enumerate(f):
			shift = max(0,int(math.log10(i+1))-1) # calculate shift to correct for topas formatting
			if line.startswith('}'):
				raise StopIteration
			else:
				if not line.startswith('iprm'):
					lst_not_iprm.append(i)
					names.append(line[0:21].strip())
				yield line[26+shift:]

	for line in f:
		if line.startswith('C_matrix_normalized'):
			f.next()
			f.next()

			print 'Ignoring reflection intensities (iprm***), because they are always correlated.'
			corr = np.genfromtxt(yield_corrmat(f),delimiter=4)
			corr = corr[lst_not_iprm,:][:,lst_not_iprm]

			return corr,names

	f.seek(0)
	return np.loadtxt(f), names


def parse_xrdml(fn):
	"""Very basic function to read panalytical XPERT PRO files (XML)
	Only parses file to get intensities and data range"""

	from xml.dom import minidom
	xmldoc = minidom.parse(fn)

	counts = xmldoc.getElementsByTagName('intensities')[0]  # grab element
	counts = map(float, counts.firstChild.wholeText.split())     # get first node + convert to float

	for rangenode in xmldoc.getElementsByTagName('positions'):
		if rangenode.getAttribute('axis') == '2Theta':
			break
		else:
			rangenode = None
	if not rangenode:
		raise IOError, "Cannot find range node in xrdml file."

	r_min = float(rangenode.getElementsByTagName('startPosition')[0].firstChild.wholeText)
	r_max = float(rangenode.getElementsByTagName('endPosition')[0].firstChild.wholeText)
	steps = len(counts)

	th2 = np.linspace(r_min,r_max, steps)

	xy = np.vstack([th2,counts]).T

	d = Data(xy,name=fn)

	root,ext = os.path.splitext(fn)
	new = root+'.xy'
	if not os.path.isfile(new):
		d.print_pattern(name=new)

	return d


def parse_iza_code(code):
	"""Takes IZA code and returns path to cif"""

	fn = code.upper()+'0.cif'
	path = os.path.join(LINESDIR,'zeolite_database',fn)

	print 'Framework code {} -> {}'.format(code, path)
	print

	return path


def run_cif2xy(cif, wl=1.0):
	import subprocess as sp

	sp.call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cif2xy.py"), "--wavelength={}".format(wl), cif])
	root,ext = os.path.splitext(cif)
	basename = os.path.basename(root)
	return basename+".xy"


def parse_xrs(f,return_as='d_xrs'):
	xy = np.array([],dtype=float).reshape(0,2)
	start = True
	finish = False
	pre = []
	post = []

	x = []
	y = []
	esd = []

	for line in f:
		# print start,finish

		# if 'finish' in line.lower() or 'end' in line.lower():
		# 	finish = True
			
		# 	# Takes care of new xrs files with no bgvalu commands
		# 	start = False
		# 	post.append(line)
		# elif line.lower().startswith('bgvalu') and not finish:
		# 	start = False
		# 	x,y = [float(item) for item in line.split()[1:]]
		# 	xy = np.append(xy,[[x],[y]],axis=1)
		# elif start:
		# 	pre.append(line)
		# elif finish or not start:
		# 	post.append(line)

		if 'finish' in line.lower() or 'end' in line.lower():
			# Takes care of new xrs files with no bgvalu commands
			start = False
			post.append(line)
		elif line.lower().startswith('bgvalu') and start:
			inp = line.split()
			x.append(float(inp[1]))
			y.append(float(inp[2]))
			try:
				esd.append(float(inp[3]))
			except IndexError:
				esd.append(np.nan)
		elif start:
			pre.append(line)
		elif not start:
			post.append(line)

	f.close()

	if return_as == 'xye':
		return np.vstack([x,y,esd]).T
	elif return_as == 'xy':
		return np.vstack([x,y]).T
	elif return_as == 'd':
		xye = np.vstack([x,y,esd]).T
		d = Data(xye,name='stepco.inp')
		return d
	elif return_as == 'd_xrs':   # include xrs stepco input data
		xye = np.vstack([x,y,esd]).T
		d = Data(xye,name='stepco.inp')
		xrs = [f.name,pre,post]
		return d,xrs
	else:
		raise SyntaxError





def parse_crplot_dat(f):
	"""Parses crplot.dat file"""
		
	# skip first 2 lines
	f.next()
	f.next()

	ret = []

	for line in f:
		inp = line.split()
		if not f:
			continue
		ret.append([float(val) for val in inp])

	return ret

def parse_hkl_dat(f):
	ret = []

	for line in f:
		inp = line.split()
		if not f:
			continue
		if len(inp) < 4:
			inp = (line[0:3],line[3:6],line[6:9],line[9:])
		else:
			ret.append([float(val) for val in inp])

	return ret


def plot_stdin(fig,update_time=0.2):
	import time
	TclError =  matplotlib.backends.backend_tkagg.tkagg.Tk._tkinter.TclError

	print 'Reading stdin.\n'

	def nrange(n=0):
		while True:
			yield n
			n=n+1

	iterator = (n for n in nrange())

	#fig = plt.figure()
	ax = fig.add_subplot(111)

	x = []
	y = []
	
	l1, = ax.plot(x,y,label='stdin')

	plt.legend()
	fig.show()

	t0 = time.time()

	while True:
		try:
			line = sys.stdin.readline()
		except KeyboardInterrupt as e:
			print e
			break
		
		if line == '':
			try:
				fig.canvas.flush_events() # update figure to prevent slow responsiveness
			except TclError:
				print '-- Window closed (TclError on readline).'
				break

			try:
				time.sleep(0.05) # prevent high cpu usage
			except KeyboardInterrupt as e:
				print e
				break
			else:
				continue
		
		inp = line.split()

		try:
			y.append(float(inp[1]))
			x.append(float(inp[0]))
		except IndexError:
			x.append(iterator.next())
			y.append(float(inp[0]))
		
		if time.time() - t0 > update_time:
			# drawing is slow, better to refresh ever x seconds
			
			t0 = time.time()

			l1.set_xdata(x)
			l1.set_ydata(y)
			
			ax.relim()
			ax.autoscale()
			
			plt.draw()
			
			try:
				fig.canvas.flush_events() # update figure to prevent slow responsiveness
			except TclError:
				print '-- Window closed (TclError on update).'
				break


def f_monitor(fin,f_init,f_update,fig=None,poll_time=0.05):
	"""experimental function for live monitoring of plots"""
	import time

	TclError =  matplotlib.backends.backend_tkagg.tkagg.Tk._tkinter.TclError

	if not fig:
		fig = plt.figure()
	
	ax = fig.add_subplot(111)

	while True:
		try:
			args = f_init(fin,fig,ax)
		except IOError:
			time.sleep(1)
		else:
			break

	plt.legend()
	fig.show()

	current_lastmod = os.stat(fin).st_mtime

	while True:
		try:
			mtime = os.stat(fin).st_mtime
		except OSError:
			time.sleep(1)
			continue

		if mtime == current_lastmod:
			# flushing here as well, to prevent locking up of mpl window			
			
			try:
				fig.canvas.flush_events()
			except TclError:
				print '-- Window closed (TclError).'
				break

			# low poll time is needed to keep responsiveness
			
			try:
				time.sleep(poll_time)
			except KeyboardInterrupt as e:
				print e
				break

		else:
			print 'Updated: {} -'.format(fin), time.ctime(os.stat(fin).st_mtime)
			current_lastmod = os.stat(fin).st_mtime
			time.sleep(0.2)
			args = f_update(fin,*args)

			#ax.relim()
			#ax.autoscale()	# resets the boundaries -> annoying for a plot that doesn't need rescaling
			plt.draw()
			
			# And this allows you to at least close the window (and crash the program by that ;))
			fig.canvas.flush_events()
		

def plot_init(fn,fig,ax):
	#f = read_file(fn)
	d = read_data(fn)

	if fn in ('fcalc_fou.xy', 'fobs_fou.xy','fcfo.out'):
		try:
			root,ext = os.path.splitext(fn)
			xl,yl = root.split('_')
		except ValueError:
			xl = 'Fobs'
			yl = 'Fcalc'

		ax.set_xlabel(xl)
		ax.set_ylabel(yl)
		ax.set_title(fn)
		line,  = ax.plot(d.x,d.y,'o',label='{} vs {}'.format(xl,yl),color='r',linestyle='')
		diag, =  ax.plot([0, 25], [0, 25], color='b', linestyle='-', linewidth=2)
		return [line,diag]
	else:
		line, = ax.plot(d.x,d.y,label=fn)
		return [line]


def plot_update(fn,*args):
	#f = read_file(fn)
	d = read_data(fn)

	if fn in ('fcalc_fou.xy', 'fobs_fou.xy','fcfo.out'):
		[line,diag] = args
		line.set_data(d.x,d.y)
		diag.set_data([0, 25], [0, 25])
		return [line,diag]
	else:
		[line] = args
		line.set_data(d.x,d.y)
		return [line]






def crplot_init(fin,fig,ax):

	fcr = open('crplot.dat','r')
	fhkl = open('hkl.dat','r')
		
	crdata = np.array(parse_crplot_dat(fcr))
	hkldata = np.array(parse_hkl_dat(fhkl))
	
	fcr.close()
	fhkl.close()

	tt = crdata[:,0]
	obs = crdata[:,1] 
	clc = crdata[:,2]
	dif = crdata[:,3]
	
	tck = hkldata[:,3]
	
	mx_dif = max(dif)
	mx_pat = max(max(obs),max(clc))
	
	pobs, = ax.plot(tt, obs, label = 'observed',c='green')
	pclc, = ax.plot(tt, clc, label = 'calculated',c='red')
	pdif, = ax.plot(tt, dif - mx_dif, label = 'difference',c='blue')
	
	pobs_zero, = ax.plot(tt,np.zeros(tt.size), c='black')
	pdif_zero, = ax.plot(tt,np.zeros(tt.size) - mx_dif, c='black')
	
	ptcks, = ax.plot(tck,np.zeros(tck.size) - (mx_dif / 4), linestyle='', marker='|', markersize=10, label = 'ticks', c='purple')
	
	args = [pobs, pclc, pdif, pobs_zero, pdif_zero, ptcks]

	return args


def crplot_update(fin,*args):
	pobs, pclc, pdif, pobs_zero, pdif_zero, ptcks = args

	fcr = open('crplot.dat','r')
	fhkl = open('hkl.dat','r')
	
	crdata = np.array(parse_crplot_dat(fcr))
	hkldata = np.array(parse_hkl_dat(fhkl))
	
	fcr.close()
	fhkl.close()

	tt = crdata[:,0]
	obs = crdata[:,1] 
	clc = crdata[:,2]
	dif = crdata[:,3]
	
	tck = hkldata[:,3]
	
	mx_dif = max(dif)
	mx_pat = max(max(obs),max(clc))

	pobs.set_data(tt,obs)
	pclc.set_data(tt,clc)
	pdif.set_data(tt,dif - mx_dif)
	pobs_zero.set_data(tt,np.zeros(tt.size))
	pdif_zero.set_data(tt,np.zeros(tt.size) - mx_dif)
	ptcks.set_data(tck,np.zeros(tck.size) - (mx_dif / 4))

	args = [pobs, pclc, pdif, pobs_zero, pdif_zero, ptcks]

	return args


def f_crplo():
	## difference data
	crplotdat = 'crplot.dat'
	fcr = open(crplotdat,'r')
	
	crdata = np.array(parse_crplot_dat(fcr))
	
	tt = crdata[:,0]
	obs = crdata[:,1] 
	clc = crdata[:,2]
	dif = crdata[:,3]
	
	mx_dif = max(dif)
	mx_pat = max(max(obs),max(clc))
	
	plt.plot(tt, obs, label = 'observed')
	plt.plot(tt, clc, label = 'calculated')
	plt.plot(tt, dif - mx_dif, label = 'difference')
	
	plt.plot(tt, np.zeros(tt.size), c='black')
	plt.plot(tt, np.zeros(tt.size) - mx_dif, c='black')

	## tick marks
	hkldat = 'hkl.dat'
	try:
		fhkl = open(hkldat,'r')
	except IOError:
		print '-- hkl.dat not found. (IOError)'
	else:
		hkldata = np.array(parse_hkl_dat(fhkl))
		tck = hkldata[:,3]
		plt.plot(tck,np.zeros(tck.size) - (mx_dif / 4), linestyle='', marker='|', markersize=10, label = 'ticks', c='purple')



def f_prf(fin):
	fin = open(fin,'r')

	for i in range(6):
		fin.next()

	tt,fobs,fcal,diff = np.genfromtxt(fin,usecols=(0,1,2,3),unpack=True)

	mx_diff = max(diff)
	mx_pat  = max(max(fobs),max(fcal))
	
	plt.plot(tt, fobs, label = 'observed')
	plt.plot(tt, fcal, label = 'calculated')
	plt.plot(tt, diff-mx_diff, label = 'difference')

	plt.plot(tt, np.zeros(tt.size), c='black')
	plt.plot(tt, np.zeros(tt.size) + (diff[0] - mx_diff), c='black')

def f_prf_init(fin,fig,ax):
	fin = open(fin,'r')

	for i in range(6):
		fin.next()

	tt,fobs,fcal,diff = np.genfromtxt(fin,usecols=(0,1,2,3),unpack=True)

	mx_diff = max(diff)
	mx_pat  = max(max(fobs),max(fcal))
	
	pfobs, = ax.plot(tt, fobs, label = 'observed')
	pfcal, = ax.plot(tt, fcal, label = 'calculated')
	pdiff, = ax.plot(tt, diff-mx_diff, label = 'difference')

	pzero_fobs, = ax.plot(tt, np.zeros(tt.size), c='black')
	pzero_diff, = ax.plot(tt, np.zeros(tt.size) + (diff[0] - mx_diff), c='black')
	
	args = [pfobs,pfcal,pdiff,pzero_fobs,pzero_diff]
	return args

def f_prf_update(fin,*args):
	pfobs,pfcal,pdiff,pzero_fobs,pzero_diff = args

	fin = open(fin,'r')

	for i in range(6):
		fin.next()
	
	tt,fobs,fcal,diff = np.genfromtxt(fin,usecols=(0,1,2,3),unpack=True)

	mx_diff = max(diff)
	mx_pat  = max(max(fobs),max(fcal))

	pfobs.set_data(tt, fobs)
	pfcal.set_data(tt, fcal)
	pdiff.set_data(tt, diff-mx_diff)
	pzero_fobs.set_data(tt, np.zeros(tt.size))
	pzero_diff.set_data(tt, np.zeros(tt.size) + (diff[0] - mx_diff))

	args = [pfobs,pfcal,pdiff,pzero_fobs,pzero_diff]
	return args




def f_plot_stepco_special(bg_xy):
	"""Specialised function for plotting XRS output, that takes an XRS data file (crplo.dat)
	and adds the background to the difference in order to make fine adjustments to the background"""

	crplotdat = 'crplot.dat'
	try:
		fcr = open(crplotdat,'r')
	except IOError:
		print '\n{} not found. Skipping difference plot.'.format(crplotdat)
	else:
		crdata = np.array(parse_crplot_dat(fcr))
		tt = crdata[:,0]
		dif = crdata[:,3]
	
		bg_interpolate = interpolate(bg_xy,tt,kind='linear')
		
		plt.plot(tt, bg_interpolate + dif, label = 'bg + diff')

def f_plot_topas_special(xyobs,xycalc,xydiff,xybg,lw=1.0):
	"""Special function that takes observed, calculated and difference plot and adds it to the background.
	This is useful to compare the difference and adjust the background accordingly"""

	if not xybg:
		raise IOError, " ** Background data not found. Please specify with --bgin"

	tt = xyobs.x

	bg_interpolate = interpolate(xybg.xy,tt,kind='linear')

	plt.plot(tt, xycalc.y + bg_interpolate, label='ycalc',lw=lw)
	#plt.plot(tt, xyobs.y  + bg_interpolate, label='yobs')
	
	plt.plot(tt, bg_interpolate + xydiff.y, label='bg + diff',lw=lw)
	plt.plot(tt, bg_interpolate, label='bg',lw=lw)

def f_plot_weighted_difference(xyobs,xycalc,xyerr,lw=1.0):
	"""Special function to calculate and display the weighted difference plot
	For more information see: Young, 'The Rietveld Method', 1993, p24-25"""

	assert xyobs.xy.shape == xycalc.xy.shape == xyerr.xy.shape, "Arrays xyobs, xycalc, and xyerr are of different shape!"

	offset = -20


	wdiff = (((xyobs.y-xycalc.y) / (xyobs.y + min(xyobs.y)+1)) / xyerr.y)
	wdiff2 = ((xyobs.y-xycalc.y) / xyerr.y)
	plt.plot(xyobs.x,wdiff+offset,label="weighted difference", lw=lw)
	plt.plot((min(xyobs.x),max(xyobs.x)),(offset,offset), c='black')


	plt.plot(xyobs.x,wdiff2+offset*2, label="weighted difference 2", lw=lw)

	#plt.plot(xyobs.x, xyobs.y-xycalc.y+offset*2, label="difference")

	plt.plot(xyobs.x, xyerr.y+offset*3, label="error")


def f_bg_correct_out(d,bg_xy,kind='linear',offset='ask',suffix_bg='_bg',suffix_corr='_corr'):
	"""Function that removes the background from a data set and prints it to a new file"""

	root,ext = os.path.splitext(d.filename)
	fn_bg   = root+suffix_bg+ext
	fn_corr = root+suffix_corr+ext

	#fn_bg   = d.filename.replace('.','_bg.')
	#fn_corr = d.filename.replace('.','_corr.')

	out_bg   = open(fn_bg,'w')
	out_corr = open(fn_corr,'w')
		
	xvals = d.x
	yvals = d.y
	
	bg_yvals = interpolate(bg_xy,xvals,kind=kind)
	
	if offset == 'ask':
		offset = raw_input("What y offset should I add to the data? (x=exit)\n >> [0] ") or 0
		offset = int(offset)
	
	if offset == 'x':
		return

	print '\nOffset = {}'.format(offset)
		
	if len(bg_xy) >= 4:
		print 'Writing background pattern to %s' % fn_bg
		for x,y in zip(xvals,bg_yvals):
			if np.isnan(y): 
				continue
			print >> out_bg, '%15.6f%15.2f' % (x,y)
		print 'Writing corrected pattern to %s' % fn_corr
				
		if d.has_esd:
			err = d.err

			for x,y,e in zip(xvals,yvals-bg_yvals+offset,err):
				if np.isnan(y): 
					continue
				print >> out_corr, '%15.6f%15.2f%15.6f' % (x,y,e)
		else:
			for x,y in zip(xvals,yvals-bg_yvals+offset):
				if np.isnan(y): 
					continue
				print >> out_corr, '%15.6f%15.2f' % (x,y)
	else:
		raise IndexError, 'Not enough values in background array, need at least 4 points.'



def new_stepco_inp(xy,name,pre,post,esds=None):
	"""Function for writing stepco input files"""

	print 'Writing xy data to file {}'.format(name)

	f = open(name,'w')

	for line in pre:
		print >> f, line,

	if np.any(esds):
		esds = esds.reshape(1,-1)

		for (x,y,esd) in np.vstack((xy,esds)).T:
			if np.isnan(esd):
				esd = ''
			else:
				esd = '{:15.2f}'.format(esd)
			print >> f, 'BGVALU    {:15f}{:15.2f}{}'.format(x,y,esd)
	else:	
		for x,y in xy.T:
			print >> f, 'BGVALU    {:15f}{:15.2f}'.format(x,y)

	for line in post:
		print >> f, line,

	f.close()



def interpolate(arr,xvals,kind='cubic'):
	"""
	arr is the data set to interpolate, can be ndim=2 array, or tuple/list of x/y values
	
	xvals are the values it has to be interpolated to
	
	kind is the type of correction, Valid options: 'linear','nearest','zero', 
	'slinear', 'quadratic, 'cubic') or as an integer specifying the order 
	of the spline interpolator to use.
	"""

	try:
		arr.ndim
	except AttributeError:
		x,y = arr
	else:
		assert arr.ndim == 2, 'Expected 2 dimensional array'
		x = arr[:,0] # create views
		y = arr[:,1] #

	try:
		kind = int(kind)
	except ValueError:
		if x.shape[0] < 4:
			kind = 'linear'
	else:
		if x.shape[0] < kind+1:
			kind = 'linear'
	
	res = interp1d(x,y,kind=kind,bounds_error=False)

	# if the background seems to take shortcuts in linear mode, this is because fixed steps
	# were set in the Backgrounder class

	return res(xvals)

def smooth(x,window_len=11,window='hanning'):
	"""smooth the data using a window with requested size.
	
	This method is based on the convolution of a scaled window with the signal.
	The signal is prepared by introducing reflected copies of the signal 
	(with the window size) in both ends so that transient parts are minimized
	in the begining and end part of the output signal.
	
	input:
		x: the input signal 
		window_len: the dimension of the smoothing window; should be an odd integer
		window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
			flat window will produce a moving average smoothing.

	output:
		the smoothed signal
		
	example:

	t=linspace(-2,2,0.1)
	x=sin(t)+randn(len(t))*0.1
	y=smooth(x)
	
	see also: 
	
	numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
	scipy.signal.lfilter
 
	TODO: the window parameter could be the window itself if an array instead of a string  

	FROM: http://www.scipy.org/Cookbook/SignalSmooth
	"""

	if x.ndim != 1:
		raise ValueError, "smooth only accepts 1 dimension arrays."
	
	if x.size < window_len:
		raise ValueError, "Input vector needs to be bigger than window size."
	
	if window_len<3:
		return x
	
	if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
		raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
	
	s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
	
	if window == 'flat': #moving average
		w=np.ones(window_len,'d')
	else:  
		w=eval('np.'+window+'(window_len)')
	
	y=np.convolve(w/w.sum(),s,mode='same')
	
	return y[window_len:-window_len+1]


def savitzky_golay(y, window_size=11, order=2, deriv=0):
	r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
	The Savitzky-Golay filter removes high frequency noise from data.
	It has the advantage of preserving the original shape and
	features of the signal better than other types of filtering
	approaches, such as moving averages techhniques.
	Parameters
	----------
	y : array_like, shape (N,)
		the values of the time history of the signal.
	window_size : int
		the length of the window. Must be an odd integer number.
	order : int
		the order of the polynomial used in the filtering.
		Must be less then `window_size` - 1.
	deriv: int
		the order of the derivative to compute (default = 0 means only smoothing)
	Returns
	-------
	ys : ndarray, shape (N)
		the smoothed signal (or it's n-th derivative).
	Notes
	-----
	The Savitzky-Golay is a type of low-pass filter, particularly
	suited for smoothing noisy data. The main idea behind this
	approach is to make for each point a least-square fit with a
	polynomial of high order over a odd-sized window centered at
	the point.
	Examples
	--------
	t = np.linspace(-4, 4, 500)
	y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
	ysg = savitzky_golay(y, window_size=31, order=4)
	import matplotlib.pyplot as plt
	plt.plot(t, y, label='Noisy signal')
	plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
	plt.plot(t, ysg, 'r', label='Filtered signal')
	plt.legend()
	plt.show()
	References
	----------
	.. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
	   Data by Simplified Least Squares Procedures. Analytical
	   Chemistry, 1964, 36 (8), pp 1627-1639.
	.. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
	   W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
	   Cambridge University Press ISBN-13: 9780521880688

	FROM: http://www.scipy.org/Cookbook/SavitzkyGolay
	"""
	try:
		window_size = np.abs(np.int(window_size))
		order = np.abs(np.int(order))
	except ValueError, msg:
		raise ValueError("window_size and order have to be of type int")
	if window_size % 2 != 1 or window_size < 1:
		raise TypeError("window_size size must be a positive odd number")
	if window_size < order + 2:
		raise TypeError("window_size is too small for the polynomials order")
	order_range = range(order+1)

	half_window = (window_size -1) // 2
	# precompute coefficients
	b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
	m = np.linalg.pinv(b).A[deriv] # coefficients

	# pad the signal at the extremes with
	# values taken from the signal itself
	firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
	lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
	y = np.concatenate((firstvals, y, lastvals))
	return np.convolve( m, y, mode='valid')


def wavelength_info(wl):
	"""Little summary for given wavelength"""

	energy = wavelength2energy(wl)

	print "wavelength: {:.5f} angstrom".format(wl)
	print "energy:     {:.5f} kev".format(energy)

	dvals = 10/np.linspace(1,10,10)

	theta2 = d2twotheta(dvals,wl)
	qvals  = 4*(np.pi/wl) * np.sin(np.radians(theta2/2))

	print "\n         d        th2          q"
	for d,th2,q in zip(dvals,theta2,qvals):
		print "{:10.3f} {:10.3f} {:10.3f}".format(d,th2,q)
	print

def calc_agreement(o,c,bg=0,kind='linear'):
	"""Calculates agreement values for given data data."""
	if np.any(bg):
		bg = interpolate(bg.T, c.x,kind=kind)  # need linear or better here

	oy = interpolate(o.xy, c.x,kind='nearest') - bg  # nearest is fast and accurate, anything else is very slow
	# oe = interpolate(o.xye[:,0:3:2],c.x,kind='nearest')

	rp = np.sum(np.abs(oy - c.y)) / np.sum(oy) # profile R-value
	
	# w = (1/oe)**2
	# rwp = ( np.sum(w*(oy - c.y)**2) / np.sum(w*(oy)**2) )**0.5 # weighted profile R-value

	return rp



class Data(object):
	total = 0
	plot_range = None

	"""container class for x,y, err data"""
	def __init__(self,arr,name=None,quiet=False, is_ticks=False):
		if not quiet:
			print 'Loading data: {}\n       shape: {}'.format(name,arr.shape)

		self.is_ticks = is_ticks

		if self.plot_range:
			r0, r1 = self.plot_range
			self.arr = arr[np.logical_and(arr[:,0]>=r0, arr[:,0]<=r1)]
		else:
			self.arr = arr

		try:
			self.x   = self.arr[:,0]
			self.y   = self.arr[:,1]
			self.xy  = self.arr[:,0:2]
			self.xye = self.arr[:,0:3]
		except IndexError:
			raise IOError, "Could not load file/data: {}".format(name)

		try:
			self.err = self.arr[:,2]
		except IndexError:
			self.err = None
			self.has_esd = False
		else:
			if np.all(self.err == np.nan):
				self.has_esd = False
				self.err = None
			else:
				self.has_esd = True

		self.index = self.total
		self.filename = name
		Data.total += 1

		if not quiet and not is_ticks:
			n = len(self.x)			# observations
			if self.has_esd:
				w = 1/self.err**2   # weights
			else:
				w = 1/(np.abs(self.y)+0.1)		# weights = y^-1 if no esds
			print '       R_exp: {:.3f}%'.format(100 * ((n) / np.sum(w*self.y**2))**0.5)

	def bin(self,binsize=0.01):
		x = self.x
		y = self.y
		fn = self.filename

		print 'Binning {} from 2th = {} - {} with a bin size of {}'.format(fn,min(x),max(x),binsize)
		print
		print 'N(x) = ', x.shape
		print 'N(y) = ', y.shape
		
		bins = np.arange(min(x),max(x),binsize)
		
		print 'N(bins) =', bins.shape
		print
		
		digi = np.digitize(x,bins)
				
		xbinned = np.array([x[digi == i].mean() for i in range(1, len(bins))])
		ybinned = np.array([y[digi == i].mean() for i in range(1, len(bins))])
		
		xbinned.shape = (-1,1)
		ybinned.shape = (-1,1)

		root,ext = os.path.splitext(self.filename)
		name = root+'_bin_'+str(binsize)+ext

		if self.has_esd:
			interpolated_errors = interpolate((self.x,self.err),xbinned, kind='linear')
			return Data(np.hstack((xbinned,ybinned,interpolated_errors)),name=name)
		else:
			return Data(np.hstack((xbinned,ybinned)),name=name)

	def smooth(self,window='savitzky_golay',window_len=7,order=3,suffix='_smooth'):
		assert window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman','savitzky_golay', 'moving_avg']

		print ' >> Applying filter: {}, window: {}, order {} (SG only) to {}'.format(window,window_len,order,self.filename)

		if window == 'savitzky_golay':
			y = savitzky_golay(self.y,window_size=window_len,order=order)
		else:
			y = smooth(self.y,window_len=window_len,window=window)

		root,ext = os.path.splitext(self.filename)
		name = root+suffix+ext
		
		x = np.copy(self.x)

		y.shape = (-1,1)
		x.shape = (-1,1)

		return Data(np.hstack((x,y)),name=name)

	def convert_wavelength(self,wavelength_in,wavelength_out):
		"""Converts 2theta values to a different wavelength"""
		print
		print " ** Convert {} from {:.4f} ANG ({:.2f} keV) to {:.4f} ANG ({:.2f} keV)".format(self.filename, wavelength_in, wavelength2energy(wavelength_in), wavelength_out, wavelength2energy(wavelength_out))
		print
		d = twotheta2d(self.x,wavelength_in)
		theta2 = d2twotheta(d,wavelength_out)
		arr = self.arr
		arr[:,0] = theta2
		return Data(arr,name=self.filename)


	def print_pattern(self,name=None,tag=""):
		"""print self (x,y,e) to 3 column file. If no name is given, original file is overwritten.
		A tag can be added to modify the original filename instead (ie. data.xye -> data_binned.xye)"""

		if tag:
			tag = "_" + tag

		if not name:
			root,ext = os.path.splitext(self.filename)
			name = root + tag + ext
		np.savetxt(name,self.xye,fmt='%15.5f')

		print 'Pattern written to {}'.format(name)

	def plot(self,ax):
		ax.plot(self.x,self.y)


class Background():
	sensitivity = 8

	def __init__(self,fig,d=None, outfunc=None,bg_correct=False, quiet=False, out=None, npick=-1, topas_bg=False, xrs=None):
		"""Class that captures mouse events when a graph has been drawn, stores the coordinates
		of these points and draws them as a line on the screen. Can also remove points and print all
		the stored points to stdout

		http://matplotlib.sourceforge.net/users/event_handling.html
		http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot

		Takes:
		a figure object
		optional numpy array with background coordinates, shape = (2,0)

		xy: 2d ndarray, shape(2,0) with x,y data"""

		self.npick = npick

		self.out = out
		self.ax = fig.add_subplot(111)
		self.topas_bg = topas_bg
		self.xrs = xrs

		# if xy is None:
		# 	self.xy = np.array([],dtype=float).reshape(2,0)
		# else:
		# 	idx = xy[0,:].argsort()
		# 	self.xy = xy[:,idx]

		if d:
			self.d  = d
			self.xy = np.array(self.d.xy,copy=True).T
		else:
			self.d  = None
			self.xy = None

		try:
			idx = self.xy[0,:].argsort()
			self.xy = self.xy[:,idx]
		except (IndexError, ValueError, TypeError):
			self.xy = np.array([],dtype=float).reshape(2,0)

		self.line, = self.ax.plot(*self.xy,lw=0.5,marker='s',mec='red',mew=2,mfc='None',markersize=5,picker=self.sensitivity,label='interactive background')

		self.pick  = self.line.figure.canvas.mpl_connect('pick_event', self.onpick)
		self.cid   = self.line.figure.canvas.mpl_connect('button_press_event', self)

		self.keyevent = self.line.figure.canvas.mpl_connect('key_press_event', self.onkeypress)

		self.n = 0

		self.tb = plt.get_current_fig_manager().toolbar

		if self.topas_bg:
			self.last_agreement = 0

		print
		print 'Left mouse button: add point'
		print 'Right mouse button: remove point'
		print 'Middle mouse button or press "a": print points to file/stdout'
		print
		print 'Note: Adding/Removing points disabled while using drag/zoom functions.'
		print

		self.bg_correct = bg_correct
		if self.bg_correct:
			self.bg_range = np.arange(self.xy[0][0],self.xy[0][1],0.01) # Set limited range to speed up calculations
			self.bg, = self.ax.plot(self.d.x,self.d.y,label='background')
			#print self.bg_range

	def __call__(self,event):
		"""Handles events (mouse input)"""
		# Skips events outside of canvas
		if event.inaxes!=self.line.axes:
			return
		# Skips events if any of the toolbar buttons are active	
		if self.tb.mode!='':
			return
		
		xdata = event.xdata
		ydata = event.ydata
		x,y = event.x, event.y

		button = event.button
		#print event

		if button == 1: #lmb
			self.add_point(x,y,xdata,ydata)
		if button == 2: # mmb
			self.printdata()
		if button == 3: # rmb
			pass
		
		if self.bg_correct and button:
			self.background_update()
	
		self.line.set_data(self.xy)
		self.line.figure.canvas.draw()


		if len(self.xy.T) == self.npick:
			print '\nClosing window...'
			import time
			time.sleep(1)
			plt.close()



	def onpick(self,event):
		"""General data point picker, should work for all kinds of plots?"""
		if not event.mouseevent.button == 3: # button 3 = right click
			return

		ind = event.ind

		removed = self.xy[:,ind]
		self.xy = np.delete(self.xy,ind,1)

		if self.topas_bg:
			agreement = calc_agreement(self.xyobs, self.xycalc, self.xy,kind=self.bg_correct)
			difference = agreement - self.last_agreement
			self.last_agreement = agreement
			string = '{:.4f} ({:+.4f})'.format(agreement,difference)
		else:
			string = ""

		for n in range(len(ind)):
			print '   --- {:.4f} {:.4f}          {}'.format(removed[:,n][0], removed[:,n][1], string)


	def onkeypress(self,event):
		if event.key == 'x':
			print 'x pressed'
		if event.key == 'y':
			print 'y pressed'
		if event.key == 'z':
			print 'z pressed'
		if event.key == 'a':
			print '\na pressed'
			self.printdata()
	

	def add_point(self,x,y,xdata,ydata):
		"""Store both data points as relative x,y points. The latter are needed to remove points"""

		self.xy = np.append(self.xy,[[xdata],[ydata]],axis=1)
		idx = self.xy[0,:].argsort()
		self.xy = self.xy[:,idx]
		
		if self.topas_bg:
			agreement = calc_agreement(self.xyobs, self.xycalc, self.xy, kind=self.bg_correct)
			difference = agreement - self.last_agreement
			self.last_agreement = agreement
			string = '{:.4f} ({:+.4f})'.format(agreement,difference)
		else:
			string = ""

		print '+++    {:.4f} {:.4f}          {}'.format(xdata, ydata, string)

	

	def background_update(self):
		xy = self.xy.T

		if xy.shape[0] < 2:
			self.bg.set_data([],[])
			return

		bg_vals = interpolate(xy,self.bg_range,kind=self.bg_correct)
		self.bg.set_data(self.bg_range,bg_vals)

	def get_esds(self):
		"""Returns None if no esds are present on the background, otherwise, it tries to interpolate the esds already present
		The esds should be specified (manually) in the background beforehand."""
		
		if self.d == None:
			return None

		if self.d.has_esd:
			print '\nAttempting to interpolate standard deviations... for new background\n'
			esds = interpolate(self.d.xye[:,0:3:2], self.xy[0], kind='linear')

			#print esds
		else:
			esds = None

		return esds
		

	def printdata(self, fout=None):
		"""Prints stored data points to stdout"""  # TODO: make me a method on class Data()
		if not self.xy.any():
			print 'No stored coordinates.'
			return None

		# print 'End'

		if not fout:
			fout = self.out

		esds = self.get_esds()
		# print esds

		if self.xrs:				
			new_stepco_inp(self.xy,*self.xrs_out,esds=esds)
		else:
			fout = open(fout,'w')
			for x,y in self.xy.transpose():
				print >> fout, '%15.6f%15.2f' % (x,y)


class Lines(object):
	"""docstring for Lines"""
	def __init__(self, fig, hide=False):
		super(Lines, self).__init__()
		if hide:
			self.plot = self.black_hole
			self.plot_tick_marks = self.black_hole
		else:
			self.fig = fig
			self.ax = self.fig.add_subplot(111)

		self.normalize = False
		self.nomove = False
		self.linewidth = 1.0
		

		#self.fig.canvas.mpl_connect('pick_event', self.onpick)

	def onpick(self):
		"""General data point picker, should work for all kinds of plots?"""
		pass

	def plot(self,data,lw=None):
		n = data.index

		if not lw:
			lw = self.linewidth

		#colour = 'bgrcmyk'[n%7]

		ax = self.ax
		label = data.filename

		if self.normalize:
			scale = np.trapz(data.y,data.x)
			print ' >> Scaling {} by 1/{:.5f}'.format(data.filename,scale)
			data.y = data.y / scale
			# print scale
		#elif 'x_ycalc_no_sda.xy' in data.filename or 'ssz61_am_corr.xye' in data.filename:
		#	scale = 500
		#	print ' >> Arbitrarily scaling {} {:.5f}  [ hardcoded, line {}: lines.plot() ]'.format(data.filename,scale,lineno())
		#	data.y = data.y * scale

		#scl = 1
		#if 'esd' in data.filename:
		#	scl = 20

		if self.nomove:
			ax.plot(data.x,data.y,label=label,lw=lw)
		else:
			dx, dy = 0/72., 64/72.

			dx *= data.index
			dy *= data.index
			offset = transforms.ScaledTranslation(dx, dy, self.fig.dpi_scale_trans)
			transform = ax.transData + offset
	
			# transform broken as of matplotlib 1.2.0, because it doesn't rescale the view
			ax.plot(data.x,data.y,transform=transform,label=label,lw=lw)

			ax.axis([data.x.min(),data.x.max()*1.2,data.y.min(),data.y.max()*1.2])

	def plot_tick_marks(self,data,i=0):
		ax = self.ax

		label = data.filename

		dx, dy = 0, -16*(i+1)/72.0

		offset = transforms.ScaledTranslation(dx, dy, self.fig.dpi_scale_trans)
		transform = ax.transData + offset

		ax.plot(data.x,data.y,transform=transform,c='black',label=label,linestyle='',marker='|',markersize=15)
		#plt.plot(tck,np.zeros(tck.size) - (mx_dif / 4), linestyle='', marker='|', markersize=10, label = 'ticks', c='purple')

	def plot_ticks_scaled(self,data):
		ax = self.ax
		label = data.filename
		ax.vlines(data.x,-100,data.y)

	def plot_boxes(self,fname):
		"""http://stackoverflow.com/questions/6895935/data-plotting-in-boxes-with-python
		http://matplotlib.org/api/artist_api.html#matplotlib.patches.Rectangle"""
		from matplotlib import patches
		
		ax = self.ax
		lw = self.linewidth
		alpha = 0.6
	
		boxes = np.loadtxt(fname,unpack=True)
		print 'Loading boxes: {}\n        shape: {}'.format(fname,boxes.shape)

		y1 = 0
	
		for x1,x2,y2 in boxes.T:
			# Class matplotlib.patches.Rectangle(xy, width, height, **kwargs)
			rect = patches.Rectangle((x1,y1), x2-x1, y2,edgecolor='red',facecolor='none',lw=lw,alpha=alpha)
			ax.add_patch(rect)

	def black_hole(*args,**kwargs):
		pass

def plot_correlation_matrix(arr,labels=[]):
	def formatter(arr,x,y,labels):
		if labels:
			print '{:4}{:4}{:8} {} {}'.format(x,y, arr[x,y], labels[x], labels[y])
		else:
			print '{:4}{:4}{:8}'.format(x,y, arr[x,y])

	def onpick(event):
		x,y = int(event.mouseevent.xdata), int(event.mouseevent.ydata)
		formatter(arr,x,y,labels)

	threshold = np.max(abs(arr)) * 0.8
	first = True

	for x,y in np.argwhere(abs(arr) > threshold):
		if y > x or x == y:
			continue
		if first:
			print '\n Highly correlated parameters (>{}):'.format(threshold)
			first = False
		formatter(arr,x,y,labels)

	pcolor = plt.pcolor(arr,picker=10)
	
	pick  = pcolor.figure.canvas.mpl_connect('pick_event', onpick)

	plt.xlim(0,arr.shape[0])
	plt.ylim(0,arr.shape[1])
	plt.colorbar()
	plt.show()


def setup_interpolate_background(d,name='bg (--correct)'):
	print 'Interpolation mode for background correction\n'
	print 'The highest and lowest values are added by default for convenience. In the case that they are removed, only the values in the background range will be printed.\n'
	
	x1 = d.x[0]
	x2 = d.x[-1]
	y1 = d.y[0]
	y2 = d.y[-1]
	
	#print x1,x2,y1,y2
	xy = np.array([[x1,y1],[x2,y2]],dtype=float)

	return Data(xy,name=name)


def f_peakdetect(d,lookahead=10,noise=5000):
	import peakdetect as pd
	from functools import partial

	_max, _min = pd.peakdetect(d.y, d.x, lookahead=lookahead, delta=noise)
	xm = [p[0] for p in _max]
	ym = [p[1] for p in _max]
	xn = [p[0] for p in _min]
	yn = [p[1] for p in _min]


	fig = plt.figure()
	ax = fig.add_subplot(111)
	d.plot(ax)

	peaks, = ax.plot(xm,ym, marker='o', lw=0, markeredgecolor='red', markerfacecolor='None', markersize=20)

	class Okp(object):
		"""docstring for okp"""
		def __init__(self, noise, lookahead):
			self.noise = noise
			self.lookahead = lookahead
			self.noisestep = 0
			self.lookaheadstep = 0

			print '1,2,3 = lookahead +/-/step'
			print '1,2,3 = noise +/-/step'

			printer('lookahead  = {}({}), noiselevel = {}({})'.format(self.lookahead,[1,10,100][self.lookaheadstep%3],self.noise,[1,10,100][self.noisestep%3]))


		def onkeypress(self,event):
			if event.key == 'q':
				self.lookahead += [1,10,100][self.lookaheadstep%3]
			if event.key == 'w':
				self.lookahead -= [1,10,100][self.lookaheadstep%3]
				if self.lookahead < 1:
					self.lookahead = 1
			if event.key == 'e':
				self.lookaheadstep += 1
			if event.key == '1':
				self.noise += [1,10,100][self.noisestep%3]
			if event.key == '2':
				self.noise -= [1,10,100][self.noisestep%3]
				if self.noise < 0:
					self.noise = 0
			if event.key == '3':
				self.noisestep += 1

			printer('lookahead  = {}({}), noiselevel = {}({})'.format(self.lookahead,[1,10,100][self.lookaheadstep%3],self.noise,[1,10,100][self.noisestep%3]))

			_max, _min = pd.peakdetect(d.y, d.x, lookahead=self.lookahead, delta=self.noise)
			xm = [p[0] for p in _max]
			ym = [p[1] for p in _max]
	
			peaks.set_data(xm,ym)
			plt.draw()

	okp = Okp(noise,lookahead)
	
	#lines.ax.plot(xn,yn, marker='o', lw=0, markeredgecolor='blue', markerfacecolor='None', markersize=4)
	fig.canvas.mpl_connect('key_press_event', okp.onkeypress)
	plt.show()

	xm,ym = peaks.get_data()
	print

	print '         2theta      intensity'
	for x,y in zip(xm,ym):
		print '%15.4f%15.4f' % (x,y)
	#print xm,ym

	return xm,ym
	


def f_identify(d,refs,criterium=0.05,lookahead=10,noise=5000):
	import operator


	print d.filename

	print lookahead,noise

	if lookahead and noise:
		import peakdetect as pd
		_max, _min = pd.peakdetect(d.y, d.x, lookahead=lookahead, delta=noise)
		xm = [p[0] for p in _max]
		ym = [p[1] for p in _max]
		print 'rawr'
	else:
		xm,ym = f_peakdetect(d)

	xm = np.array(xm)
	ym = np.array(ym)


	lst = []

	for fn in refs:
		#ref = read_data(fn,usecols=4,append_zeros=True,savenpy=False)
		ref = load_tick_marks(fn,col=4)

		diff_array = np.abs(xm-ref.x[:,np.newaxis])
		
		#print diff_array
		#print diff_array.shape
	
		min_diff = np.amin(diff_array,0)
	
		#print min_diff
	
		da = min_diff < criterium

		# do manually
		exit()
	
		r = sum(min_diff[da]*min_diff[da]) / sum(xm[da]*xm[da])
		wr = sum(ym[da] * min_diff[da]*min_diff[da]) / sum(ym[da]*xm[da]*xm[da])
		missing = len(xm) - sum(da)

		lst.append((r,wr,missing,ref.filename))
		

	lst = sorted(lst, key=operator.itemgetter(2), reverse=True)


	print lst
	for (r,rw,missing,fn) in lst:
		print '{:6.3f} {:6.3f} using: {} refs --> {}'.format(r,wr,missing, fn)
		


def f_compare(data,kind=0,reference=None):
	import itertools
	import scipy.stats
	import operator

	def calc_combined_value(spearmanr,kendallr,pearsonr):
		spearmanr = spearmanr if not np.isnan(spearmanr) else 1.0
		kendallr  = kendallr  if not np.isnan(kendallr ) else 1.0
		pearsonr  = pearsonr  if not np.isnan(pearsonr ) else 1.0

		return pearsonr**(1/3.0)*kendallr**(1/3.0)*spearmanr**(1/3.0)




	start,stop,step = 2,25.00,0.01 # parameters used for calculated pattern
	
	min_tt = 0		# boundary for check
	max_tt = 2300	# should not excede number of parameters

	#shuffle = (-100,-80,-60,-40,-20,0,20,40,60,80,100)
	shuffle = (0,)
	max_shift = max(shuffle)
	min_shift = min(shuffle)



	xvals = np.arange(start,stop,step)
	# resample at same step rate as calculated pattern
	data = [Data(np.vstack((xvals,interpolate(d.xy,xvals,kind='linear'))).T,name=d.filename,quiet=True) for d in data]


	#for d in data:
	#	print d.xy.shape

	if reference:
		reference = Data(np.vstack((xvals,interpolate(reference.xy,xvals,kind='linear'))).T,name=reference.filename)
		pairs = ((reference,d) for d in data)
		l = float(len(data))
		lfill = len(reference.filename.split('/')[-1])
		rfill = max(len(d.filename.split('/')[-1]) for d in data)
	else:
		lfill = rfill = max(len(d.filename.split('/')[-1]) for d in data)
		pairs = itertools.combinations(data,2)
		l = float(len(data)*(len(data)-1)/2)
	#pairs = itertools.combinations_with_replacement(data,2)

	lst = []

	print "Calculate agreement for {} combinations of {} patterns.".format(int(l),len(data))
	

	for i,(d1,d2) in enumerate(pairs):
		printer("{:2.0f}%".format(i/l*100))

		names = "{:<{lfill}} - {:<{rfill}}".format(d1.filename.split('/')[-1], d2.filename.split('/')[-1],lfill=lfill,rfill=rfill)

		for shift in shuffle:
			pearsonr,pearsonp = scipy.stats.pearsonr(   d1.y[min_tt-min_shift+shift:max_tt-max_shift+shift],   d2.y[min_tt-min_shift+shift:max_tt-max_shift+shift])
			kendallr,kendallp  = scipy.stats.kendalltau(d1.y[min_tt-min_shift+shift:max_tt-max_shift+shift:5], d2.y[min_tt-min_shift+shift:max_tt-max_shift+shift:5])
			spearmanr,spearmanp = scipy.stats.spearmanr(d1.y[min_tt-min_shift+shift:max_tt-max_shift+shift],   d2.y[min_tt-min_shift+shift:max_tt-max_shift+shift])
			
			if pearsonr <= 0 or kendallr <= 0 or spearmanr <= 0:
				continue
		
			#if pearsonp > 0.01 or kendallp > 0.01 or spearmanp > 0.01:
			#	continue
			
			combined = calc_combined_value(pearsonr,kendallr,spearmanr)
	
			lst.append((combined,spearmanr,kendallr,pearsonr,spearmanp,kendallp,pearsonp,shift*step,names))

	printer("")
	print

	lst = sorted(lst, key=operator.itemgetter(kind))

	print '2theta range = {:8.3f} {:8.3f}'.format(start+min_tt*step,start+max_tt*step)
	print 'Shuffle values by {}'.format([shift*step for shift in shuffle])

	print'combined spearman     pval  kendall     pval  pearson     pval    shift -> sorted by {}'.format(['combined', 'spearman', 'kendall', 'pearson'][kind])   
	for (combined,spearmanr,kendallr,pearsonr,spearmanp,kendallp,pearsonp,shift,names) in lst:
		print "{:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}   ".format(combined, spearmanr, spearmanp, kendallr, kendallp, pearsonr, pearsonp, shift) + names


def calc_fwhm(uvw):
	u,v,w = uvw
	th2      = np.linspace(0,70,70*50)
	th_rad   = np.radians(th2 / 2)

	fwhm = (u*np.tan(th_rad)**2 + v*np.tan(th_rad) + w)**0.5

	xy = np.vstack([th2,fwhm]).T

	return Data(xy, 'UVW')



def fix_sls_data(data, quiet=False):	
	"""Input list of Data objects, all of them will be processed and written to:
	filename_fixed.xye"""
		
	print
	print '------------'
	print 'FIX SLS DATA'
	print '------------'
	print
	print 'esds are calculated as:'
	print 'esd = sqrt(Yobs/scale) * sqrt(1/N) * scale'
	print
	print 'Yobs:  input pattern'
	print 'scale: scale factor between raw counts (.raw) and corrected data (.dat)'
	print 'N:     number of raw patterns merged'
	print 
	print 'Estimated scale by rearranging above formula:'
	print '(assuming background is correct)'
	print
	print 'scale = (N/Yobs) * esd^2'

	if not isinstance(data,list):
		data = list((data,))

	scl = raw_input('\nScale (leave blank for picking procedure) \n >> ')
	npats = raw_input('\nNumber of raw patterns \n >> [16]') or 16
	#scl = 1.3
	npats = float(npats)**0.5

	for i in range(len(data)):
		d = data[i]
		i += 1
		if 'esd' in d.filename: continue

		assert d.has_esd, '\n *** Data file {} contains no standard deviations!!'.format(d.filename)
			
		if not scl:
			print '\nPick 3 background points'
			print 'These will be used to estimate the scale factor'
			print
	
			fig = plt.figure()
			bg = Background(fig,d=None,quiet=quiet,npick=3)
			lines = Lines(fig,hide=quiet)
			lines.plot(d)
			plt.legend()
			plt.show()
	
			points = bg.xy.T
	
			avg = []
			for x,v in points:
				idx = find_nearest(d.x,x)
				scl1 = d.err[idx]**2 * (npats**2 / d.y[idx])
				avg.append(scl1)
				print '{:10.4f}**2 * ({:d} / {:10.4f}) = {:10.4f}'.format(d.err[idx],int(npats**2),d.y[idx],scl1)
			scl = np.mean(avg)
		else:
			scl = float(scl)
			
		print
		print 'Npats =', int(npats**2)
		print 'Scale =', scl
		print

		err = scl*(1/npats)*(d.y/scl)**0.5
		d2 = np.copy(d.xye)
		d2 = Data(np.vstack((d.x,d.y,err)).T,name=d.filename)
		d2.print_pattern(tag='fixed')
		data.append(d2)

def find_nearest(array,value):
	"""Find index of nearest value"""
	idx = (np.abs(array-value)).argmin()
	return idx

def twotheta2d(twotheta,wavelength):
	theta = np.radians(twotheta / 2)
	d = wavelength / (2*np.sin(theta))
	return d

def d2twotheta(d,wavelength):
	theta = np.degrees(np.arcsin((wavelength) / (2*d)))
	return 2*theta

def wavelength2energy(wl):
	"""Takes wavelength in Angstrom, returns energy in keV"""
	# 1E3 from ev to kev, divide by 1E10 from angstrom to meter
	return 1E10*planck_constant*speed_of_light/(wl*1E3*elementary_charge)

def energy2wavelength(E):
	"""Takes wavelength in keV, returns energy in Angstrom"""
	# 1E3 from ev to kev, divide by 1E10 from angstrom to meter
	return 1E10*planck_constant*speed_of_light/(E*1E3*elementary_charge)

def plot_reciprocal_space(fnobs, fncalc=None, orthogonal_view=True):
	from mpl_toolkits.mplot3d import Axes3D

	if orthogonal_view == True:
		from mpl_toolkits.mplot3d import proj3d
	
		def orthogonal_proj(zfront, zback):
			a = (zfront+zback)/(zfront-zback)
			b = -2*(zfront*zback)/(zfront-zback)
			return np.array([[1,0,0,0],
							[0,1,0,0],
							[0,0,a,b],
							[0,0,0,zback]])
	
		print " >> Orthogonal view at least breaks automatic placement of axis labels."
		proj3d.persp_transformation = orthogonal_proj

	def onkeypress(event):
		if event.key == 'x':
			ax.view_init(0,0)
			plt.draw()
		if event.key == 'y':
			ax.view_init(0,-90)
			plt.draw()
		if event.key == 'z':
			ax.view_init(90,-90)
			plt.draw()

	if fncalc:
		if not isinstance(fncalc,str):
			raise TypeError
		calc = np.loadtxt(fncalc)
		calc = set([tuple(map(int,row[0:3])) for row in calc])
	
	if isinstance(fnobs,str):
		fnobs = [fnobs]
	
	try:
		obs = [np.loadtxt(fn) for fn in fnobs] 
	except ValueError:
		obs = [np.genfromtxt(fn,delimiter=[4,4,4,8,8]) for fn in fnobs]
	obs  = [set([tuple(map(int,row[0:3])) for row in data]) for data in obs]


	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.set_xlabel('h')
	ax.set_ylabel('k')
	ax.set_zlabel('l')
	fig.canvas.mpl_connect('key_press_event', onkeypress)
	print ' >> Press x,y,z to align view along specified axis.'

	for i,data in enumerate(obs):
		if fncalc:
			diff = calc - data
			absent = data - calc
			data = data & calc

		label = fnobs[i]

		h,k,l = zip(*data)
		ax.plot(h,k,l,'b.',label = label+' observed', ms=2.50)

		# # Feeble attempt at getting heatmaps to work
		# hhm,hxe,hye = np.histogram2d(k,l,bins=50)
		# khm,kxe,kye = np.histogram2d(l,h,bins=50)
		# lhm,lxe,lye = np.histogram2d(h,k,bins=50)

		# hm = np.meshgrid(hxe,hye)
		# km = np.meshgrid(kxe,kye)
		# lm = np.meshgrid(lxe,lye)

		# ax.contour(hm[0],hm[1],hhm, zdir='x',offset=min(h))
		# ax.contour(km[0],km[1],khm, zdir='y',offset=min(k))
		# ax.contour(lm[0],lm[1],lhm, zdir='z',offset=min(l))

		if fncalc:
			h,k,l = zip(*diff)
			ax.plot(h,k,l,'ro',label = label+' missing',mfc='None',mec='red')
			if len(absent) > 0:
				h,k,l = zip(*absent) 
				ax.plot(h,k,l,'r+',label = label+' sys. absent')
				# ax.plot(h,k,l,'b.',label = label+' observed', ms=2.50)
			else:
				print ' >> 0 systematic absences'
	plt.legend()
	plt.show()


def main():
	usage = """"""

	description = """Notes:
- Requires numpy and matplotlib for plotting.
- Scipy is needed for some interpolation functions.
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
						help="Paths to input files.")
		
	parser.add_argument("-s", "--shift",
						action="store_false", dest="nomove",
						help="Slightly shift different plots to make them more visible (useful to make a waterfall plot).")

	parser.add_argument("-i","--bgin",
						action="store", type=str, dest="bg_input",
						help="Initial points for bg correction (2 column list; also works with stepco.inp). Overwrites the file with updated coordinates.")

	# parser.add_argument("-t", "--ticks",
						# action='store', type=str, nargs='?', dest="plot_ticks", const='hkl.dat',
						# help="Specify tick mark file. If no argument is given, lines defaults to hkl.dat")

	parser.add_argument("-t", "--ticks",
						action='store', type=str, nargs='*', dest="plot_ticks",
						help="Specify tick mark file. Assuming list of 2 theta values. Special value => hkl.dat. Specify column with --tc")

	parser.add_argument("-r", "--range",
						action='store', type=float, nargs=2, dest="plot_range",
						help="Specify plot range for data files.")

	parser.add_argument("-c", "--bgcorrect", metavar='OPTION',
						action="store", type=str, dest="bg_correct",
						help="Starts background correction routine. Only the first pattern listed is corrected. Valid options: 'linear','nearest','zero', 'slinear', 'quadratic, 'cubic') or as an integer specifying the order of the spline interpolator to use. Recommended: 'cubic'.")

	parser.add_argument("--bin", metavar='binsize',
						action="store", type=float, dest="bin",
						help="Bins the patterns supplied with the supplied bins and prints binned data sets.")

	parser.add_argument("--compare", metavar='x',
						action="store", type=int, nargs='?', dest="compare", const=1,
						help="Calculates similarity between data sets. For now, background needs to be removed manually beforehand. Sort by VAL: 1 = combined, 2 = spearman, 3 = kendall's tau, 4 = pearson.")

	parser.add_argument("-m", "--monitor", metavar='FILE',
						action="store", type=str, dest="monitor",
						help="Monitor specified file and replots if the file is updates. First 2 columns are plotted. Supports .prf files from FullProf. Special value: crplot.dat")

	parser.add_argument("--topasbg",
						action="store_true", dest="topas_bg",
						help="Generally applicable background correction procedure mainly for use with Topas. Reads x_ycalc.xy, x_ydiff.xy which can be output using macros Out_X_Ycalc(x_ycalc.xy) and Out_X_Difference(x_ydiff.xy). The background is reconstructed using the linear interpolation from --bgin. Recommended usage: lines pattern.xye -c linear --bgin bg_points.xy --topasbg")

	parser.add_argument("-n", "--normalize",
						action="store_true", dest="normalize_all",
						help="Normalize the values of all data sets by dividing by their integrated intensity")

	
#	parser.add_argument("-o,--bgout",
#						action="store", type=str, dest="bg_input",
#						help="Filename to output background points to.")


	group_xrs = parser.add_argument_group('XRS',description="Command line options specific to XRS-82")


	group_xrs.add_argument("-x", "--xrs", metavar='FILE',
						action="store", type=str, nargs='?', dest="xrs", const='stepco.inp',
						help="xrs stepco file to open and alter. Default = stepco.inp")

	group_xrs.add_argument("--crplo",
						action="store_true", dest="crplo",
						help="Mimics crplo -- plots observed, calculated and difference pattern and tick marks")

	group_xrs.add_argument("--stepco",
						action="store_true", dest="stepco",
						help="Shortcut for lines stepscan.dat -x stepco.inp. Additionally, plots the previous background and the background + the difference plot. Reads difference data from crplot.dat")


	group_adv = parser.add_argument_group('Advanced options')

	group_adv.add_argument("-q", "--quiet",
						action="store_true", dest="quiet",
						help="Don't plot anything and reduce verbosity.")

	group_adv.add_argument("--tc",
						action='store', type=int, dest="plot_ticks_col", metavar='col',
						help="Which column to use for plotting of tick marks. First column = 1. Default = 3, for hkl.dat files")

	parser.add_argument("-T", "--Ticks",
						action='store', type=str, nargs='+', dest="plot_ticks_scaled",
						help="Plots ticks scaled to the intensity. Expects .xy files with 2 columns, 2th/I")
	
	parser.add_argument("--convert",
						action='store', type=parse_wl, nargs='+', dest="convert_2theta",metavar="WL",
						help="Convert powder pattern to a different wavelength [wavelength_in wavelength_out]. If no diffraction pattern is given, the program will give a small summary for the wavelengths/energies provided")

	group_adv.add_argument("--ref", metavar='FILE',
						# action="store", type=str, nargs='*', dest="compare_reference",
						action="store", type=str, dest="compare_reference",
						help="Reference pattern to check against all patterns for --compare")

	group_adv.add_argument("--boxes", metavar='FILE',
						action="store", type=str, dest="boxes",
						help="Plots boxes from data in given file. Format should be: 2theta_min, 2theta_max,intensity")
		
	group_adv.add_argument("--savenpy",
						action="store_true", dest="savenpy",
						help="Convert input data sets to numpy binary format for faster loading on next run (extension = .npy). Default = False.")
	
	group_adv.add_argument("--smooth",
						action="store", type=str, dest="smooth",
						help="Smooth data set according to smoothing algorithm given. Choice from: 'flat', 'hanning', 'hamming', 'bartlett', 'blackman','savitzky_golay', 'moving_avg'.")

	group_adv.add_argument("--peakdetect",
						action="store", type=int, nargs=2, dest="peakdetect",
						help="Use peak detection algorithm")

	group_adv.add_argument("--lw","--linewidth",
						action="store", type=float, dest="linewidth",
						help="Set linewidth of the plot")

	group_adv.add_argument("--corrmat",
						action="store", type=str, dest="corrmat",
						help="Plot given file as correlation matrix (expects ascii file with a n*m matrix). Can also take a Topas output file if a matrix has been generated with keyword C_matrix_normalized.")	

	group_adv.add_argument("--identify",
						action="store", type=float, dest="identify",
						help="Identify given data sets against sets of d-spacings given by --reference")

	group_adv.add_argument("--nobg",
						action="store_false", dest="backgrounder",
						help="Turns off background module."	)

	group_adv.add_argument("--plot_esd",
						action="store_true", dest="plot_esd",
						help="Plots observed intensities and esds for given xye file (exepcts 3 column data).")

	group_adv.add_argument("--savefig",
						action="store", type=str, nargs='?', dest="savefig", const='figure1.png',
						help="Saves figure as png instead of displaying it")

	group_adv.add_argument("--fixsls",
						action="store_true", dest='fixsls',
						help="Fix SLS data sets and exit")

	group_adv.add_argument("--rec3d",
						action="store", type=str, nargs='*', dest='rec3d',
						help="Plot the first 3 columns (h k l) of given file in 3d. If no filenames are given, 'args' are taken. If 2 files are given, the first should be the observed ones and the second should be the calculated ones.")

	group_adv.add_argument("--capillary",
						action="store", type=str, dest='capillary',
						help="Give capillary file to be subtracted from the pattern.")

	group_adv.add_argument("--uvw", metavar=("U","V","W"),
						action="store", type=float, nargs=3, dest='plot_uvw',
						help="Plot FWHM = (U.tan(theta)^2 + V.tan(theta) + W)^0.5")

	group_adv.add_argument("--wavelength",
						action="store", type=parse_wl, dest='wavelength',
						help="Specify the wavelength to use for the powder pattern generation. Default = 1.0 Angstrom")

	group_adv.add_argument("--wyd, --weighted_ydiff",
						action="store_true", dest='weighted_ydiff',
						help="Display weighted difference plot. Requires x_yobs.xy, x_ycalc.xy, x_yerr.xy")
	
	parser.set_defaults(backgrounder = True,
						xrs = None,
						nomove = True,
						normalize_all = False,
						bg_correct = False,
						crplo = False,
						christian = False,
						monitor = None,
						plot_ticks = False,
						plot_ticks_col = 1,
						stepco = False,
						topas_bg = False,
						compare = False,
						compare_reference = None,
						quiet = False,
						bg_input = None,
						bg_output = None,
						bg_offset = 0,
						boxes = None,
						bin = None,
						## advanced options
						show = True,
						convert_2theta = None,
						linewidth = 1.0,
						savenpy = False,
						smooth = False,
						peakdetect = False,
						corrmat = None,
						savefig = False,
						plot_esd = False,
						fixsls = False,
						rec3d = None,
						ipython = False,
						capillary = None,
						uvw = None,
						wavelength = 1.0,
						#special
						weighted_ydiff = False,
						guess_filetype=True) 
	
	options = parser.parse_args()
	args = options.args

	if options.stepco:
		options.xrs = 'stepco.inp'
		args = ['stepscan.dat']
	if options.bg_input:
		copyfile(options.bg_input, options.bg_input+'~')
		options.bg_output = options.bg_input

	Data.plot_range = options.plot_range

	if options.guess_filetype:
		prf = [arg for arg in args if arg.endswith('.prf')]
		for fn in prf:
			args.remove(fn)
		spc = [arg for arg in args if '.spc' in arg]
		for fn in spc:
			args.remove(fn)
	else:
		prf,spc = None,None

	if options.rec3d:
		print options.rec3d, type(options.rec3d)
		if options.rec3d == 'args':
			plot_reciprocal_space(fnobs = args, fncalc = None)
		elif len(options.rec3d) == 1:
			plot_reciprocal_space(fnobs = options.rec3d[0], fncalc = None)
		elif len(options.rec3d) == 2:
			plot_reciprocal_space(fnobs = options.rec3d[0], fncalc = options.rec3d[1])

		else:
			raise ValueError
		exit()

	data = [read_data(fn,savenpy=options.savenpy,wl=options.wavelength) for fn in args] # returns data objects

	if options.capillary:
		capillary = read_data(options.capillary)
		smoothed = capillary.smooth(window='hanning',window_len=101)
		for d in data:
			print ' >> Removing contribution of {} from {}'.format(options.capillary,d.filename)
			f_bg_correct_out(d,smoothed.xy,kind=options.bg_correct,offset=0,suffix_corr='_rem_cap')
		exit()

	if options.plot_esd:
		data.extend([read_data(fn,usecols=(0,2),suffix=' esd') for fn in args])
	if spc:
		data.extend([read_data(fn,usecols=(0,2),suffix=' -DIFFaX',savenpy=options.savenpy) for fn in spc])

	if options.convert_2theta:
		if data:
			wl_in,wl_out = options.convert_2theta
			data = [d.convert_wavelength(wl_in,wl_out) for d in data]
			for d in data:
				d.print_pattern(tag='{:.2f}'.format(wl_out))
		else:
			for wl in options.convert_2theta:
				wavelength_info(wl)
			exit()

	if options.fixsls:
		fix_sls_data(data, quiet=options.quiet)
		exit()

	if options.corrmat:
		f = open(options.corrmat)
		corr,labels = get_correlation_matrix(f)
		plot_correlation_matrix(corr,labels)
		exit()

	if options.identify:
		if options.peakdetect:
			lookahead,noise = options.peakdetect
		else:
			lookahead,noise = None,None

		for d in data:
			f_identify(d,options.compare_reference,lookahead=lookahead,noise=noise)
	elif options.peakdetect:
		#options.show = False
		lookahead,noise = options.peakdetect
		for d in data:
			f_peakdetect(d,lookahead=lookahead,noise=noise)

	if options.xrs:
		fname = options.xrs
		copyfile(fname,fname+'~')
		f = read_file(fname)
		bg_data,options.xrs_out = parse_xrs(f)
	elif options.bg_input:
		try:
			bg_data = read_data(options.bg_input)
		except:
			bg_data = setup_interpolate_background(data[0],name=options.bg_input)
	else:
		bg_data = None


	fig = plt.figure()
	lines = Lines(fig,hide=options.quiet)
	lines.nomove = options.nomove
	lines.normalize = options.normalize_all
	lines.linewidth = options.linewidth
	lines.savefig = options.savefig
	
	if plt.get_backend() == 'TkAgg':
		fig.tight_layout(rect=(0,0,1,1))  ## tight layout, smaller gray border

	if options.quiet or options.fixsls or options.monitor:
		pass
	elif options.bg_correct:
		if not bg_data:
			bg_data = setup_interpolate_background(data[0])
		bg = Background(fig,d=bg_data,bg_correct=options.bg_correct, quiet=options.quiet, out=options.bg_output, topas_bg=options.topas_bg, xrs=options.xrs) 
	elif options.backgrounder:
		bg = Background(fig,d=bg_data,quiet=options.quiet, topas_bg=options.topas_bg, xrs=options.xrs)

	if options.crplo:
		f_crplo()

	if prf:	# fullprof profile files
		for fn in prf:
			f_prf(fn)

	if options.compare:
		if options.compare_reference:
			ref = read_data(options.compare_reference)
			lines.plot(ref,lw=lines.linewidth*2)
		else:
			ref = None

		kind = options.compare-1
		f_compare(data,kind=kind,reference=ref)

	#plt.plot(range(10),range(10))
	#plt.show()
	#plt.plot(range(5),range(5,10))
	#plt.show()

	if options.plot_ticks_scaled:
		for fn in options.plot_ticks_scaled:
			d = read_data(fn,savenpy=False)
			lines.plot_ticks_scaled(d)


	if options.quiet:
		pass
	else:
		for d in reversed(data):
			lines.plot(d)

	if options.plot_uvw:
		d = calc_fwhm(options.plot_uvw)
		lines.plot(d)

	if options.plot_ticks:
		for i,hkl_file in enumerate(options.plot_ticks):
			col = 4 if options.plot_ticks == 'hkl.dat' else options.plot_ticks_col - 1
			ticks = load_tick_marks(hkl_file,col=col)
			if ticks:
				lines.plot_tick_marks(ticks,i=i)

	if options.weighted_ydiff:
		try:
			xyobs  = read_data('x_yobs.xy')
			xycalc = read_data('x_ycalc.xy')
			xyerr  = read_data('x_yerr.xy')
		except IOError,e:
			print e
			print
			print """Please add the following lines to the TOPAS input file to generate the needed files:
	Out_X_Yobs(x_yobs.xy)          
	Out_X_Ycalc(x_ycalc.xy)       
	Out_X_Yerr(x_yerr.xy)   
			"""
			exit(0)
		f_plot_weighted_difference(xyobs,xycalc,xyerr,lw=options.linewidth)

	if options.topas_bg:
		try:
			xyobs  = read_data('x_yobs.xy')
			xycalc = read_data('x_ycalc.xy')
			xydiff = read_data('x_ydiff.xy')
			#xybg   = read_data('x_ybg.xy')
		except IOError,e:
			print e
			print
			print """Please add the following lines to the TOPAS input file to generate the needed files:
	Out_X_Yobs(x_yobs.xy)          
	Out_X_Ycalc(x_ycalc.xy)       
	Out_X_Difference(x_ydiff.xy)   
			"""
			exit(0)

		f_plot_topas_special(xyobs,xycalc,xydiff,bg_data,lw=options.linewidth)
		# specifying bg.xycalc and bg.xyobs is necessary to update the Rp value on every step
		bg.xycalc = xycalc
		bg.xyobs  = data[0]


	if options.stepco:
		assert bg_data, "No background data available, can't use option --stepco!"

		lines.plot(bg_data)
		f_plot_stepco_special(bg_data.xy)

	if options.bin:
		for d in reversed(data):
			dbinned = d.bin(options.bin)
			dbinned.print_pattern()
			lines.plot(dbinned)
	
	if options.smooth:
		for d in reversed(data):
			dsmooth = d.smooth(options.smooth) # smoothing performed in place
			dsmooth.print_pattern()
			lines.plot(dsmooth)

	if options.boxes:
		lines.plot_boxes(options.boxes)



	if options.quiet or not options.show:
		pass
	elif not sys.stdin.isatty():
		plot_stdin(fig)
	elif options.monitor:
		if options.monitor in ('crplot.dat','crplot'):
			f_monitor('crplot.dat',crplot_init,crplot_update,fig=fig)
		elif options.monitor.endswith('.prf'):
			f_monitor(options.monitor,f_prf_init,f_prf_update,fig=fig)

		else:
			fn = options.monitor
			f_monitor(fn,plot_init,plot_update,fig=fig)
	elif options.savefig:
		plt.legend()
		out = options.savefig
		plt.savefig(out, bbox_inches=0)
	else:
		plt.legend()
		plt.show()


	if options.bg_correct:
		#for d in data:
		#	f_bg_correct_out(d=d,bg_xy=bg.xy.T,offset=options.bg_offset)
	
		f_bg_correct_out(d=data[0],bg_xy=bg.xy.T,kind=bg_correct,offset=options.bg_offset)
	
	try:
		if bg.xy.any():
			bg.printdata(fout='lines.out')
	except UnboundLocalError:
		pass


if __name__ == '__main__':
	main()
