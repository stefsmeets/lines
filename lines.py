#!/usr/bin/env python2.7-32

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

__version__ = '21-02-2013'


params = {'legend.fontsize': 10,
		  'legend.labelspacing': 0.1}
plt.rcParams.update(params)


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



def read_data(fn,usecols=None,append_zeros=False,savenpy=False):
	if fn == 'stepco.inp':
		f = read_file(fn)
		return parse_xrs(f,return_as='d')

	root,ext = os.path.splitext(fn)
	
	try:
		#raise IOError
		inp = np.load(root+'.npy')
	except (IOError, AssertionError):
		try:
			inp = np.loadtxt(fn,usecols=usecols,ndmin=2)
		except IOError,e:
			print e
			exit(0)
	else:
		ext = '.npy'
		fn = root+'.npy'

	if append_zeros:
		(i,j) = inp.shape
		inp = np.hstack((inp,np.zeros((i,1))))

	if inp.shape[1] > 3:
		print 'More than 3 columns read from {}, assuming x,y,esd, ignoring the rest.'.format(f.name)

	d = Data(inp,name=fn)

	if savenpy and ext != '.npy':
		np.save(root,inp)

	return d

def load_tick_marks(path,col=3):
	"""Checks if file exists and loads tick mark data as data class. Use column=3 default for xrs"""
	print path

	try:
		f = open(path,'r')
		f.close()
	except IOError:
		print '-- {} not found. (IOError)'.format(path)
		return None

	ticks = read_data(path,usecols=(col,),append_zeros=True)
	return ticks

def get_correlation_matrix(f,topas=False):
	names = []
	def yield_corrmat(f):
		for i,line in enumerate(f):
			shift = max(0,int(math.log10(i+1))-1) # calculate shift to correct for topas formatting
			if line.startswith('}'):
				raise StopIteration
			else:
				names.append(line[0:21].strip())
				yield line[26+shift:]

	for line in f:
		if line.startswith('C_matrix_normalized'):
			f.next()
			f.next()
			corr = np.genfromtxt(yield_corrmat(f),delimiter=4)
			return corr,names

	f.seek(0)
	return np.loadtxt(f), names


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
	elif return_as == 'd_xrs':
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


def f_monitor(fn,f_init,f_update,fig=None,poll_time=0.05):
	"""experimental function for live monitoring of plots"""
	import time

	TclError =  matplotlib.backends.backend_tkagg.tkagg.Tk._tkinter.TclError

	if not fig:
		fig = plt.figure()
	
	ax = fig.add_subplot(111)

	args = f_init(fn,fig,ax)

	plt.legend()
	fig.show()

	current_lastmod = os.stat(fn).st_mtime

	while True:
		if os.stat(fn).st_mtime == current_lastmod:
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
			print 'Updated:', time.ctime(os.stat(fn).st_mtime)
			current_lastmod = os.stat(fn).st_mtime

			args = f_update(fn,*args)

			#ax.relim()
			#ax.autoscale()	# resets the boundaries -> annoying for a plot that doesn't need rescaling
			plt.draw()
			
			# And this allows you to at least close the window (and crash the program by that ;))
			fig.canvas.flush_events()
		

def plot_init(fn,fig,ax):
	f = read_file(fn)
	d = read_data(f)
	f.close()

	line, = ax.plot(d.x,d.y,label=fn)

	return [line]


def plot_update(fn,*args):
	[line] = args

	f = read_file(fn)
	d = read_data(f)
	f.close()

	line.set_data(d.x,d.y)

	return [line]


def crplot_init(fn,fig,ax):

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
	
	pobs, = ax.plot(tt, obs, label = 'observed')
	pclc, = ax.plot(tt, clc, label = 'calculated')
	pdif, = ax.plot(tt, dif - mx_dif, label = 'difference')
	
	pobs_zero, = ax.plot(tt,np.zeros(tt.size), c='black')
	pdif_zero, = ax.plot(tt,np.zeros(tt.size) - mx_dif, c='black')
	
	ptcks, = ax.plot(tck,np.zeros(tck.size) - (mx_dif / 4), linestyle='', marker='|', markersize=10, label = 'ticks', c='purple')
	
	args = [pobs, pclc, pdif, pobs_zero, pdif_zero, ptcks]

	return args


def crplot_update(fn,*args):
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


def f_plot_stepco_special(bg_xy):
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

def f_plot_topas_special(xyobs,xycalc,xydiff,xybg):
	tt = xyobs.x

	bg_interpolate = interpolate(xybg.xy,tt,kind='linear')

	plt.plot(tt, xycalc.y + bg_interpolate, label='ycalc')
	#plt.plot(tt, xyobs.y  + bg_interpolate, label='yobs')
	
	plt.plot(tt, bg_interpolate + xydiff.y, label='bg + diff')
	plt.plot(tt, bg_interpolate, label='bg')






def f_bg_correct_out(d,bg_xy,offset='ask'):
	root,ext = os.path.splitext(d.filename)
	fn_bg = root+'_bg'+ext
	fn_corr = root+'_corr'+ext


	fn_bg   = d.filename.replace('.','_bg.')
	fn_corr = d.filename.replace('.','_corr.')
	out_bg   = open(fn_bg,'w')
	out_corr = open(fn_corr,'w')
		
	xvals = d.x
	yvals = d.y
	
	bg_yvals = interpolate(bg_xy,xvals,kind=options.bg_correct)
	
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


class Data(object):
	total = 0

	"""container class for x,y, err data"""
	def __init__(self,arr,name=None,quiet=False):
		if not quiet:
			print 'Loading data: {}\n       shape: {}'.format(name,arr.shape)

		self.arr = arr
		self.x   = self.arr[:,0]
		self.y   = self.arr[:,1]
		self.xy  = self.arr[:,0:2]
		self.xye = self.arr[:,0:3]

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

	def smooth(self,window='savitzky_golay',window_len=7,order=3):
		assert window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman','savitzky_golay', 'moving_avg']

		if window == 'savitzky_golay':
			y = savitzky_golay(self.y,window_size=window_len,order=order)
		else:
			y = smooth(self.y,window_len=window_len,window=window)

		root,ext = os.path.splitext(self.filename)
		name = root+'_smooth'+ext
		
		x = np.copy(self.x)

		y.shape = (-1,1)
		x.shape = (-1,1)

		return Data(np.hstack((x,y)),name=name)


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

	def __init__(self,fig,d=None, outfunc=None,bg_correct=False, quiet=False, out=None):
		"""Class that captures mouse events when a graph has been drawn, stores the coordinates
		of these points and draws them as a line on the screen. Can also remove points and print all
		the stored points to stdout

		http://matplotlib.sourceforge.net/users/event_handling.html
		http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot

		Takes:
		a figure object
		optional numpy array with background coordinates, shape = (2,0)

		xy: 2d ndarray, shape(2,0) with x,y data"""

		self.out = out
		self.ax = fig.add_subplot(111)
		
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

		self.line, = self.ax.plot(*self.xy,lw=0.5,marker='s',mec='red',mew=1,mfc='None',markersize=3,picker=self.sensitivity,label='interactive background')

		self.pick  = self.line.figure.canvas.mpl_connect('pick_event', self.onpick)
		self.cid   = self.line.figure.canvas.mpl_connect('button_press_event', self)

		self.keyevent = self.line.figure.canvas.mpl_connect('key_press_event', self.onkeypress)

		self.n = 0

		self.tb = plt.get_current_fig_manager().toolbar


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


	def onpick(self,event):
		"""General data point picker, should work for all kinds of plots?"""
		if not event.mouseevent.button == 3: # button 3 = right click
			return

		ind = event.ind

		removed = self.xy[:,ind]
		self.xy = np.delete(self.xy,ind,1)

		for n in range(len(ind)):
			print '   --- {} {}'.format(*removed[:,n])


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

		print '+++    {} {}'.format(xdata, ydata)

		self.xy = np.append(self.xy,[[xdata],[ydata]],axis=1)
		idx = self.xy[0,:].argsort()
		self.xy = self.xy[:,idx]
	

	def background_update(self):
		xy = self.xy.T

		if xy.shape[0] < 2:
			self.bg.set_data([],[])
			return

		bg_vals = interpolate(xy,self.bg_range,kind=self.bg_correct)
		self.bg.set_data(self.bg_range,bg_vals)
		

	def printdata(self):
		"""Prints stored data points to stdout"""  # TODO: make me a method on class Data()
		if not self.xy.any():
			print 'No stored coordinates.'
			return None

		print '---'
		if options.xrs:
			if self.d.has_esd:
				print '\nAttempting to interpolate standard deviations... for new stepco.inp\n'

				esds = interpolate(self.d.xye[:,0:3:2], self.xy[0], kind='linear')

				#print esds

			new_stepco_inp(self.xy,*options.xrs_out,esds=esds)
		elif self.out:
			out = open(self.out,'w')
			for x,y in self.xy.transpose():
				print >> out, '%15.6f%15.2f' % (x,y)
		else:
			for x,y in self.xy.transpose():
				print '%15.6f%15.2f' % (x,y)


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
		

		#self.fig.canvas.mpl_connect('pick_event', self.onpick)

	def onpick(self):
		"""General data point picker, should work for all kinds of plots?"""
		pass

	def plot(self,data):
		n = data.index

		colour = 'bgrcmyk'[n%7]

		ax = self.ax
		label = data.filename
		
		if options.nomove:
			ax.plot(data.x,data.y,label=label)
		else:
			dx, dy = 8/72., 8/72.

			dx *= data.index
			dy *= data.index
			offset = transforms.ScaledTranslation(dx, dy, self.fig.dpi_scale_trans)
			transform = ax.transData + offset
	
			# transform broken as of matplotlib 1.2.0, because it doesn't rescale the view
			ax.plot(data.x,data.y,transform=transform,label=label)

	def plot_tick_marks(self,data):
		ax = self.ax

		label = data.filename

		dx, dy = 0, -16/72.

		offset = transforms.ScaledTranslation(dx, dy, self.fig.dpi_scale_trans)
		transform = ax.transData + offset

		ax.plot(data.x,data.y,transform=transform,c='black',label=label,linestyle='',marker='|',markersize=10)
		#plt.plot(tck,np.zeros(tck.size) - (mx_dif / 4), linestyle='', marker='|', markersize=10, label = 'ticks', c='purple')

	def plot_ticks_scaled(self,data):
		ax = self.ax
		label = data.filename
		ax.vlines(data.x,-100,data.y)

			

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

	threshold = np.max(abs(arr)) * 0.9
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

	for fn in options.compare_reference:
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
			
			combined = pearsonr**(1/3.0)*kendallr**(1/3.0)*spearmanr**(1/3.0)
	
			lst.append((combined,spearmanr,kendallr,pearsonr,spearmanp,kendallp,pearsonp,shift*step,names))

	printer("")
	print

	lst = sorted(lst, key=operator.itemgetter(kind))

	print '2theta range = {:8.3f} {:8.3f}'.format(start+min_tt*step,start+max_tt*step)
	print 'Shuffle values by {}'.format([shift*step for shift in shuffle])

	print'combined spearman     pval  kendall     pval  pearson     pval    shift -> sorted by {}'.format(['combined', 'spearman', 'kendall', 'pearson'][kind])   
	for (combined,spearmanr,kendallr,pearsonr,spearmanp,kendallp,pearsonp,shift,names) in lst:
		print "{:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f} {:8.3f}   ".format(combined, spearmanr, spearmanp, kendallr, kendallp, pearsonr, pearsonp, shift) + names


def main(options,args):
	files = args
	data = [read_data(fn,savenpy=False) for fn in args] # returns data objects
	

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

	if options.plot_ticks:
		hkl_file = options.plot_ticks
		col = options.plot_ticks_col - 1
		ticks = load_tick_marks(hkl_file,col=col)
		if ticks:
			lines.plot_tick_marks(ticks)

	if options.quiet:
		pass
	elif options.bg_correct:
		if not bg_data:
			bg_data = setup_interpolate_background(data[0])
		bg = Background(fig,d=bg_data,bg_correct=options.bg_correct,quiet=options.quiet,out=options.bg_output) 
	elif options.backgrounder:
		bg = Background(fig,d=bg_data,quiet=options.quiet)


	if options.crplo:
		f_crplo()

	if options.compare:
		if options.compare_reference:
			ref = read_data(options.compare_reference)
			lines.plot(ref)
		else:
			ref = None

		kind = options.compare-1
		f_compare(data,kind=kind,reference=ref)

	#plt.plot(range(10),range(10))
	#plt.show()
	#plt.plot(range(5),range(5,10))
	#plt.show()

	for fn in options.plot_ticks_scaled:
		d = read_data(fn,savenpy=False)
		lines.plot_ticks_scaled(d)


	if options.quiet:
		pass
	else:
		for d in reversed(data):
			lines.plot(d)

	if options.topas_bg:
		xyobs  = read_data('x_yobs.xy')
		xycalc = read_data('x_ycalc.xy')
		xydiff = read_data('x_ydiff.xy')
		#xybg   = read_data('x_ybg.xy')

		f_plot_topas_special(xyobs,xycalc,xydiff,bg_data)


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



	if options.quiet or not options.show:
		pass
	elif not sys.stdin.isatty():
		plot_stdin(fig)
	elif options.monitor:
		if options.monitor in ('crplot.dat','crplot'):
			f_monitor('crplot.dat',crplot_init,crplot_update,fig=fig)
		else:
			fn = options.monitor
			f_monitor(fn,plot_init,plot_update,fig=fig)
	else:
		plt.legend()
		plt.show()


	if options.bg_correct:
		f_bg_correct_out(d=data[0],bg_xy=bg.xy.T,offset=options.bg_offset)




if __name__ == '__main__':
	usage = """"""

	description = """Notes:
- Requires numpy and matplotlib for plotting.
"""	
	
	epilog = 'Updated: {}'.format(__version__)
	
	parser = argparse.ArgumentParser(#usage=usage,
									description=description,
									epilog=epilog, 
									formatter_class=argparse.RawDescriptionHelpFormatter,
									version=__version__)

	parser = argparse.ArgumentParser()

	parser.add_argument("args", 
						type=str, metavar="FILE",nargs='*',
						help="Paths to input files.")
		
	parser.add_argument("-s", "--shift",
						action="store_false", dest="nomove",
						help="Slightly shift different plots to make them more visible. **Broken with matplotlib 1.2.0+")

	parser.add_argument("-i","--bgin",
						action="store", type=str, dest="bg_input",
						help="Initial points for bg correction (2 column list; also works with stepco.inp). Overwrites the file with updated coordinates.")

	parser.add_argument("-t", "--ticks",
						action='store', type=str, nargs='?', dest="plot_ticks", const='hkl.dat',
						help="Specify tick mark file. If no argument is given, lines defaults to hkl.dat")


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
						help="Monitor specified file and replots if the file is updates. First 2 columns are plotted. Special value: crplot.dat")

	parser.add_argument("--topasbg",
						action="store_true", dest="topas_bg",
						help="Generally applicable background correction procedure mainly for use with Topas. Reads x_ycalc.xy, x_ydiff.xy which can be output using macros Out_X_Ycalc(x_ycalc.xy) and Out_X_Difference(x_ydiff.xy). The background is reconstructed using the linear interpolation from --bgin. Recommended usage: lines pattern.xye -c linear --bgin bg_points.xy --topasbg")


	
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
						help="Plots ticks scaled to the intensity.")

	group_adv.add_argument("--ref", metavar='FILE',
						action="store", type=str, nargs='*', dest="compare_reference",
						help="Reference pattern to check against all patterns for --compare")
		
	group_adv.add_argument("--savenpy",
						action="store_true", dest="savenpy",
						help="Convert input data sets to numpy binary format for faster loading on next run (extension = .npy). Default = False.")
	
	group_adv.add_argument("--smooth",
						action="store", type=str, dest="smooth",
						help="Smooth data set according to smoothing algorithm given. Choice from: 'flat', 'hanning', 'hamming', 'bartlett', 'blackman','savitzky_golay', 'moving_avg'.")

	group_adv.add_argument("--peakdetect",
						action="store", type=int, nargs=2, dest="peakdetect",
						help="Use peak detection algorithm")

	group_adv.add_argument("--corrmat",
						action="store", type=str, dest="corrmat",
						help="Plot given file as correlation matrix (expects ascii file with a n*m matrix). Can also take a Topas output file if a matrix has been generated with keyword C_matrix_normalized.")	

	group_adv.add_argument("--tcorrmat",
						action="store", type=str, dest="tcorrmat",
						help="Takes a Topas output file and plots the correlation matrix if so specified with C_matrix_normalized.")

	group_adv.add_argument("--identify",
						action="store", type=float, dest="identify",
						help="Identify given data sets against sets of d-spacings given by --reference")

	group_adv.add_argument("--nobg",
						action="store_false", dest="backgrounder",
						help="Turns off background module.")

	
	parser.set_defaults(backgrounder = True,
						xrs = None,
						nomove = True,
						bg_correct = False,
						crplo = False,
						christian = False,
						monitor = None,
						plot_ticks = False,
						plot_ticks_col = 4,
						stepco = False,
						topas_bg = False,
						compare = False,
						compare_reference = None,
						quiet = False,
						bg_input = None,
						bg_output = None,
						bg_offset = 0,
						bin = None,
						## advanced options
						show = True,
						savenpy = False,
						smooth = False,
						peakdetect = False,
						corrmat = None) 
	
	options = parser.parse_args()
	args = options.args

	if options.stepco:
		options.xrs = 'stepco.inp'
		args = ['stepscan.dat']
	if options.bg_input:
		options.bg_output = options.bg_input

	main(options,args)