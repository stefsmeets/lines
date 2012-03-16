#!/usr/bin/env python2.7-32

import argparse
try:
	import numpypy as np
except ImportError:
	import numpy as np


import matplotlib.pyplot as plt


__version__ = '16-03-2012'


def gen_read_files(paths):
	"""opens file, returns file object for reading"""
	for path in paths:
		try:
			f = open(path,'r')
		except IOError:
			print 'cannot open', path
			exit(0)
		yield f


def read_data(f):

	lines = (line.split() for line in f if line)
	lines = ([float(item) for item in line] for line in lines)
	lists = (np.array(lst) for lst in zip(*lines))

	x = lists.next()
	y = lists.next()
	
	try:
		err = lists.next()
	except StopIteration:
		err = None

	d = Data(x,y,err)
	d.filename = f.name

	return d



class Data(object):
	"""container class for x,y, err data"""
	def __init__(self,x,y,err):
		self.x = x
		self.y = y
		self.err = err		




class Background():
	sensitivity = 10


	def __init__(self,fig):
		"""Class that captures mouse events when a graph has been drawn, stores the coordinates
		of these points and draws them as a line on the screen. Can also remove points and print all
		the stored points to stdout

		http://matplotlib.sourceforge.net/users/event_handling.html
		http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot"""
		ax = fig.add_subplot(111)
		
		self.xy = np.array([],dtype=float).reshape(2,0)

		self.line, = ax.plot(*self.xy,lw=0.5,marker='s',mec='red',mew=1,mfc='None',markersize=3,picker=self.sensitivity)

		self.pick  = self.line.figure.canvas.mpl_connect('pick_event', self.onpick)
		self.cid   = self.line.figure.canvas.mpl_connect('button_press_event', self)
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
		
		# print "event: x,y,inp", x,y,button

		xdata = event.xdata
		ydata = event.ydata
		x,y = event.x, event.y

		#inv = self.ax.transData.inverted()


		#event.xdata,event.ydata <-- event.x,event.y
		#print event.x,event.y,inv.transform_point([event.x,event.y])
		#print self.ax.transData.transform_point([event.xdata,event.ydata])

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

	def add_point(self,x,y,xdata,ydata):
		"""Store both data points as relative x,y points. The latter are needed to remove points"""

		print '+++    {} {}'.format(xdata, ydata)

		self.xy = np.append(self.xy,[[xdata],[ydata]],axis=1)
		idx = self.xy[0,:].argsort()
		self.xy = self.xy[:,idx]

	
	def printdata(self):
		"""Prints stored data points to stdout

		TODO: Fix me!!!"""
		if len(self.xy) < 1:
			print 'No stored coordinates.'

		for x,y in self.xydata:
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
		ax = self.fig.add_subplot(111)
		ax.plot(data.x,data.y,c='r')










def main(options,args):

	files = gen_read_files(args)

	data = (read_data(f) for f in files) # returns data objects


	fig = plt.figure()
	
	lines = Lines(fig)

	if options.backgrounder:
		bg = Background(fig)

	for d in data:
		lines.plot(d)

	plt.show()





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
	
	
	parser.add_argument("args", 
						type=str, metavar="FILE",nargs='*',
						help="Paths to input files.")
		
#	parser.add_argument("-c", "--count",
#						action="store_true", dest="count",
#						help="Counts occurances of ARG1 and exits.")
#	
#
#	parser.add_argument("-f", "--files", metavar='FILE',
#						action="store", type=str, nargs='+', dest="files",
#						help="Sflog files to open. This should be the last argument. (default: all sflog files in current directory)")


	
	parser.set_defaults(backgrounder=True)
	
	options = parser.parse_args()
	args = options.args


	main(options,args)