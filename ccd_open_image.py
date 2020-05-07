#!/usr/bin/env python2.7

import numpy as np
import time, os, commands
from astropy.io import fits
from astropy.io.fits import getdata
import scipy.ndimage

from PIL import Image

def imageOpener(file, projection):
	Names = []
	Values = []
	Params = ''
	if '.fit' in file:
		OpenedImage, Header = getdata(str(file), 1, header=True)
		for i in range(0, len(Header)):
			if 'alar' in Header.cards[i]:
				Names.append(list(Header.cards[i])[0])
				Values.append(list(Header.cards[i])[1])
		for i in range(0, len(Names)):
			Params += (Names[i] + '\t'+Values[i] + '\n')
	elif '.ppm' in file:
		OpenedImage = np.asarray(Image.open(str(file)), dtype=np.float)[:,:,0] 
		Header = []
		Names = []
		Values = []
	
	elif '.dat' in file:
		#OpenedImage = np.asarray(Image.open(str(file)), dtype=np.float)[:,:,0] 
		OpenedImage = [[],[]]#np.zeros((480,640),dtype=int)
		data=np.genfromtxt(str(file), skip_header=7)
		a=data[:,0] # read the first column
		b=data[:,1] # read the second column
		for i in range(0, 480):
			OpenedImage = np.append(OpenedImage, b[:640])
		OpenedImage = np.reshape(OpenedImage, (480,640))
		Header = []
		Names = []
		Values = []
	
	elif '.astra' in file:
		#OpenedImage = np.asarray(Image.open(str(file)), dtype=np.float)[:,:,0] 
		OpenedImage = [[],[]]#np.zeros((480,640),dtype=int)
		data=np.genfromtxt(str(file))
		
		####################### Zero-cross data, MS3G, transverse (X - Y) projection #################
		if projection == 'AstraX':
			a=data[:,0] # read the first column
			b=data[:,1] # read the second column
			'''
			bins_y = 20
			bins_x = 400
			H, yedges, xedges = np.histogram2d(b, a, [bins_y, bins_x])
			
			m = 42.8265                         # MS3G CCD magnification factor

			Scale = (((np.abs(yedges.min() - yedges.max())*1000000)/bins_y)/m,((np.abs(xedges.min() - xedges.max())*1000000)/bins_x)/m)
				
			H = scipy.ndimage.zoom(H, Scale, order=3)
			xoff = 50
			yoff = 250

			OpenedImage = np.lib.pad(H, ((yoff, 480-yoff-int(round(bins_y*Scale[0]))), (xoff, 640-xoff-int(round(bins_x*Scale[1])))), mode='constant')
			'''
		elif projection == 'AstraZ':
			####################### MS1G, transverse (X - Y) projection #################
			'''
			a=data[:,0] # read the first column
			b=data[:,1] # read the second column
			bins_y = 20
			bins_x = 400
			H, yedges, xedges = np.histogram2d(b, a, [bins_y, bins_x])
			
			m = 42.8265                         # MS3G CCD magnification factor

			Scale = (((np.abs(yedges.min() - yedges.max())*1000000)/bins_y)/m,((np.abs(xedges.min() - xedges.max())*1000000)/bins_x)/m)
			
			H = scipy.ndimage.zoom(H, Scale, order=3)
			xoff = 50
			yoff = 250

			OpenedImage = np.lib.pad(H, ((yoff, 480-yoff-int(round(bins_y*Scale[0]))), (xoff, 640-xoff-int(round(bins_x*Scale[1])))), mode='constant')
			'''
			####################### MS1G, longitudinal (X - Z) projection #################
			
			a=data[:,2]
			b=data[:,1]
			'''
			bins_y = 20
			bins_x = 100
			H, yedges, xedges = np.histogram2d(b, a, [bins_y, bins_x])
			#X, Y = np.meshgrid((xedges[1:] + xedges[:-1]) / 2, (yedges[1:] + yedges[:-1]) / 2)
			#plt.contourf(X, Y, H, cmap='jet')

			m = 42.8265/1.8                       # MS3G CCD magnification factor
			
			#print ((np.abs(yedges.min() - yedges.max())*1000000)/bins_y)/m
			#print ((np.abs(xedges.min() - xedges.max())*1000000)/bins_x)/m
			Scale = (((np.abs(yedges.min() - yedges.max())*1000000)/bins_y)/m,((np.abs(xedges.min() - xedges.max())*1000000)/bins_x)/m)
			#Scale = (0.5,((np.abs(xedges.min() - xedges.max())*1000000)/bins_x)/m)

			H = scipy.ndimage.zoom(H, Scale, order=3)
			xoff = 200
			yoff = 0

			OpenedImage = np.lib.pad(H, ((yoff, 480-yoff-int(round(bins_y*Scale[0]))), (xoff, 640-xoff-int(round(bins_x*Scale[1])))), mode='constant')
			#H = np.lib.pad(H, ((yoff, 480-yoff-bins_y), (xoff, 640-xoff-bins_x)), mode='constant')
			'''
		
		#print a.min(), a.max()
		#print b.min(), b.max()
		
		bins_y = 120
		bins_x = 160
		H, yedges, xedges = np.histogram2d(b, a, [bins_y, bins_x])
		
		#print xedges.min(), xedges.max()
		#print yedges.min(), yedges.max()
		
		m = 10                         # ASTRA magnification factor
		Scale = (((np.abs(yedges.min() - yedges.max())*1000000)/bins_y)/m,((np.abs(xedges.min() - xedges.max())*1000000)/bins_x)/m)
		
		#print Scale
		
		H = scipy.ndimage.zoom(H, Scale, order=3)
		xoff = (640-int(round(bins_x*Scale[1])))/2
		yoff = (480-int(round(bins_y*Scale[0])))/2
		
		#print xoff, yoff
		if yoff >= 0 and xoff >=0:
			OpenedImage = np.lib.pad(H, ((yoff, yoff), (xoff, xoff)), mode='constant')
		elif yoff < 0 and xoff >=0:
			OpenedImage = np.lib.pad(H, ((0, 0), (xoff, xoff)), mode='constant')
		elif yoff >= 0 and xoff < 0:
			OpenedImage = np.lib.pad(H, ((yoff, yoff), (0, 0)), mode='constant')
		elif yoff < 0 and xoff < 0:
			OpenedImage = np.lib.pad(H, ((0, 0), (0, 0)), mode='constant')
		Header = []
		Names = []
		Values = []
	
	return OpenedImage, Params, Names, Values