#!/usr/bin/env python2.7-32

import argparse
import numpy as np


import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

__version__ = '19-03-2012'


def gen_read_files(paths):
	"""opens file, returns file object for reading"""
	for path in paths:
		try:
			f = open(path,'r')
		except IOError:
			print 'cannot open', path
			exit(0)
		yield f

def read_file(path):
	"""opens file, returns file object for reading"""
	try:
		f = open(path,'r')
	except IOError:
		print 'cannot open', path
		exit(0)
	return f

def read_data(f):
	ret = []

	for line in f:
		inp = line.split()
		if not inp:
			continue
		ret.append([float(val) for val in inp])

	lists = iter(zip(*ret))

	#lines = (line.split() for line in f if line)
	#lines = ([float(item) for item in line] for line in lines)
	#lists = (np.array(lst) for lst in zip(*lines))

	x = np.array(lists.next())
	y = np.array(lists.next())
	
	try:
		err = np.array(lists.next())
	except StopIteration:
		err = None

	d = Data(x,y,err)
	d.filename = f.name

	return d


def parse_xrs(f):
	xy = np.array([],dtype=float).reshape(2,0)
	start = True
	pre = []
	post = []

	for line in f:
		if line.lower().startswith('bgvalu'):
			start = False
			x,y = [float(item) for item in line.split()[1:]]
			xy = np.append(xy,[[x],[y]],axis=1)
		elif start:
			pre.append(line)
		elif not start:
			post.append(line)

	f.close()
	xrs = [f.name,pre,post]
	return xy,xrs


def new_stepco_inp(xy,name,pre,post):
	print 'Writing xy data to file {}'.format(name)

	f = open(name,'w')

	for line in pre:
		print >> f, line,

	for x,y in xy.transpose():
		print >> f, 'BGVALU    %15.6f%15.0f' % (x,y)

	for line in post:
		print >> f, line,

	f.close()


class Data(object):
	total = 0
	"""container class for x,y, err data"""
	def __init__(self,x,y,err):
		self.x = x
		self.y = y
		self.err = err		
		self.index = self.total
		Data.total += 1


class Background():
	sensitivity = 8

	def __init__(self,fig,xy=None,outfunc=None):
		"""Class that captures mouse events when a graph has been drawn, stores the coordinates
		of these points and draws them as a line on the screen. Can also remove points and print all
		the stored points to stdout

		http://matplotlib.sourceforge.net/users/event_handling.html
		http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot

		Takes:
		a figure object
		optional numpy array with background coordinates, shape = (2,0)"""
		ax = fig.add_subplot(111)
		
		if xy is None:
			self.xy = np.array([],dtype=float).reshape(2,0)
		else:
			self.xy = xy
			idx = self.xy[0,:].argsort()
			self.xy = self.xy[:,idx]

		self.line, = ax.plot(*self.xy,lw=0.5,marker='s',mec='red',mew=1,mfc='None',markersize=3,picker=self.sensitivity)

		self.pick  = self.line.figure.canvas.mpl_connect('pick_event', self.onpick)
		self.cid   = self.line.figure.canvas.mpl_connect('button_press_event', self)

		self.keyevent = self.line.figure.canvas.mpl_connect('key_press_event', self.onkeypress)

	


		self.tb    = plt.get_current_fig_manager().toolbar

		self.ax = ax

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

		if button == 1:
			self.add_point(x,y,xdata,ydata)
		if button == 3:
			pass
		if button == 2:
			self.printdata()
	
		self.line.set_data(self.xy)
		self.line.figure.canvas.draw()



	def onpick(self,event):
		"""General data point picker, should work for all kinds of plots?"""
		if event.mouseevent.button != 3:
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
		

	def add_point(self,x,y,xdata,ydata):
		"""Store both data points as relative x,y points. The latter are needed to remove points"""

		print '+++    {} {}'.format(xdata, ydata)

		self.xy = np.append(self.xy,[[xdata],[ydata]],axis=1)
		idx = self.xy[0,:].argsort()
		self.xy = self.xy[:,idx]
	
	def printdata(self):
		"""Prints stored data points to stdout"""
		if not self.xy.any():
			print 'No stored coordinates.'
			return None

		print '---'
		if options.xrs:
			new_stepco_inp(self.xy,*options.xrs_out)
		else:
			for x,y in self.xy.transpose():
				print '%15.6f%15.0f' % (x,y)


class Lines(object):
	"""docstring for Lines"""
	def __init__(self, fig):
		super(Lines, self).__init__()
		self.fig = fig
		
		#self.fig.canvas.mpl_connect('pick_event', self.onpick)

	def onpick(self):
		"""General data point picker, should work for all kinds of plots?"""
		pass

	def plot(self,data):
		n = data.index

		colour = 'bgrcmyk'[n%7]

		ax = self.fig.add_subplot(111)


		if options.nomove:
			dx, dy = 0, 0
		else:
			dx, dy = 8/72., 8/72.

		dx *= data.index
		dy *= data.index
		offset = transforms.ScaledTranslation(dx, dy, self.fig.dpi_scale_trans)
		transform = ax.transData + offset

		ax.plot(data.x,data.y,transform=transform,c=colour)
		



class Ticks(object):
	"""docstring for Ticks"""
	def __init__(self, arg):
		super(Ticks, self).__init__()
		self.arg = arg
		





def main(options,args):
	files = gen_read_files(args)

	data = [read_data(f) for f in files] # returns data objects

	fig = plt.figure()

	lines = Lines(fig)

	if options.xrs:
		from shutil import copyfile
		
		name = options.xrs
		copyfile(name,name+'~')
		f = read_file(name)
		xy,options.xrs_out = parse_xrs(f)
	else:
		xy = None

	if options.backgrounder:
		bg = Background(fig,xy)

	for d in reversed(data):
		lines.plot(d)

	plt.show()





if __name__ == '__main__':
	#plt.gca().get_frame().set_linewidth(2)




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
	
	
	parser.add_argument("args", 
						type=str, metavar="FILE",nargs='*',
						help="Paths to input files.")
		
#	parser.add_argument("-c", "--count",
#						action="store_true", dest="count",
#						help="Counts occurances of ARG1 and exits.")
#	
#
	parser.add_argument("-x", "--xrs", metavar='FILE',
						action="store", type=str, dest="xrs",
						help="xrs file to open and alter")

	parser.add_argument("-n", "--nomove",
						action="store_true", dest="nomove",
						help="doesn't readjust other plots")



	
	parser.set_defaults(backgrounder=True,
						xrs = None,
						nomove = False)
	
	options = parser.parse_args()
	args = options.args


	main(options,args)