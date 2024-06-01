#!/usr/bin/env python

'''
This is a simple program that uses 468/f at all band edges of interest.  Red
boxes are drawn from edge to edge indicating spans of resonance for
particular frequencies.  At resonant frequnecy highest voltage is at the end
of an end fed and difficult to match.  If you have a modest antenna tuner,
avoid these areas.  If you have a capable tuner, -use- these areas since
signal is strongest.

Bands must be in: 160,80,60,40,30,20,17,15,12,10,6 m

Usage example up to half wavelength:
  endfed.py 40 20 15 10

Usage example up to full wavelength:
  endfed.py -f 40 20 15 10

or to generate the same in meters:
  endfed.py -m 40 20 15 10

and a graph pops up.  Red areas indicate highest voltage at end of wire.
Mouse cursor can be moved on image to read values.  Image can also be saved
as a png.

Mike Markowski, ab3ap
mike.ab3ap@gmail.com
March 2024
'''

import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# USA band edges.  You might want to adjust to CW-only edges.
hamBands_MHz={
	160:np.array([1.8,	 2]),
	 80:np.array([3.5,	 4]),
	 60:np.array([5.335,  5.405]),
	 40:np.array([7,	  7.3]),
	 30:np.array([10.1,  10.15]),
	 20:np.array([14,	 14.35]),
	 17:np.array([18.068, 18.168]),
	 15:np.array([21,	 21.45]),
	 12:np.array([24.89,  24.99]),
	 10:np.array([28,	 29.7]),
	  6:np.array([50,	 54])
}

def cli(argv):
	'''Pull band values from command line.  Values are sorted in reverse
	order and for each band its low and high frequency edges are returned.

	Input:
	  string[]: command line arguments.
	Output:
	  [float[]]: list of 2-elt numpy arrays of band edge min, max in MHz.
	'''
	prog = os.path.basename(argv[0])
	argv = argv[1:]
	fullwave = metric = False
	bands = []
	i = 0
	while i < len(argv):
		if argv[i] == '-f':
			fullwave = True
		elif argv[i] == '-m':
			metric = True
		else:
			try:
				b = int(argv[i])
			except ValueError:
				usage(prog)
			bands.append(b)
		i += 1
	bands.sort(reverse=True)
	if len(bands) == 0:
		usage(prog)
	return prog, bands, metric, fullwave

def edges_MHz(prog, bands_MHz):
	e_MHz = []
	for b in bands_MHz:
		if b in [160,80,60,40,30,20,17,15,12,10,6]:
			e_MHz.append(hamBands_MHz[b])
		else:
			usage(prog)
	return e_MHz

def graph(title, edges_ft, metric, lenQtr_ft):
	'''Plot a red box for each span of resonant frequencies.
	'''
	plt.figure(figsize=(8, 1.25), dpi=120)
	plt.title(title, fontsize=10)
	plt.xlabel('Wire Length (%s)' % ('m' if metric else 'ft'))
	plt.yticks([]) # Don't label y axis.
	plt.ylim(0,1)  # Arbitrary values.
	plt.grid(True)

	if metric:
		lenQtr_ft *= 12/39.37 # Feet to meters.

	xMax = 0
	for e in edges_ft:
		if metric:
			e *= 12/39.37 # Feet to meters.
		plt.fill([e[0],e[0],e[1],e[1]], [0,1,1,0], 'r')
		xMax = max(xMax, e[1])
	plt.xlim(lenQtr_ft,xMax)
	plt.tight_layout()
	plt.show()

def high_V(band_MHz, lenMax_ft):
	'''Resonant frequencies have highest voltages at ends of antennas.
	Input:
	  band_kHz (float[]): kHz, np.array of min and max frequencies.
	  lenMax_ft (float): ft, length for largest wavelength considered.
	Output:
	  [float[]]: list of 2-elt numpy arrays of band edge min, max in MHz.
	'''

	len1_ft, len0_ft = 468/band_MHz # It's all based on this!
	multiples = int(lenMax_ft/len0_ft) # 1/2 wavelengths per lenMax_ft.
	res_ft = np.zeros((multiples, 2)) # Resonant lengths at band edge freqs.
	res_ft[:,0] = (1 + np.arange(multiples))*len0_ft
	res_ft[:,1] = (1 + np.arange(multiples))*len1_ft
	return res_ft

def usage(prog):
	print('Usage: %s [-f] [-m] band...' % prog)
	print('	  -f, graph fullwave (halfwave default).')
	print('	  -m, metric lengths.')
	print('	  band, integer in 160,80,60,40,30,20,17,15,12,10,6 m')
	print('	  E.g., %s 40 20 15 10' % prog)
	sys.exit(1)

def main(argv):
	prog, bands_m, metric, fullwave = cli(argv)
	bands_MHz = edges_MHz(prog, bands_m)

	lenQtr_ft = 234/bands_MHz[0][0] # Min length, 1/4 wavelength, required.
	if fullwave:
		lenMax_ft = 2*468/bands_MHz[0][0] # Full wavelength.
	else:
		lenMax_ft = 468/bands_MHz[0][0] # Half wavelength.

	all_ft = [np.array([0, lenQtr_ft])]
	all_ft = []
	for band_MHz in bands_MHz:
		res_ft = high_V(band_MHz, lenMax_ft)
		all_ft.extend(res_ft)
	s = str(bands_m)
	graph('High Voltage Lengths for %s m' % s[1:-1], all_ft, metric, lenQtr_ft)

if __name__ == '__main__':
	main(sys.argv)