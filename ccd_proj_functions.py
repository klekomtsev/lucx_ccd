#!/usr/bin/python

import numpy as np

def screen_slector(Screen):
	#Magnification factors and projections
	if Screen== 'UVCCD':
	 	m = 7.4                               # UV CCD magnification factor
	elif Screen == 'UVLTL':
		m = 7.4                               # UV LTL CCD magnification factor
	elif Screen == 'MS1G':
		m = 45.916                         # MS1G CCD magnification factor
	elif Screen == 'MS2G':
		m = 49.362                         # MS2G CCD magnification factor 
	elif Screen == 'CP1G':
		m = 20.942                         # CP1G CCD magnification factor 
	elif Screen == 'MS3G':
		m = 42.8265                         # MS3G CCD magnification factor
	elif Screen == 'AstraX':
		m = 10                         # MS3G CCD magnification factor
	elif Screen == 'AstraZ':
		m = 10                         # MS3G CCD magnification factor
	else:
	     m = 1
	     
	return m

def proj_func_full_image(lum_img, Screen):
	m = 	screen_slector(Screen)
	x_proj = np.sum(lum_img, axis=0) # Sum each column
	y_proj = np.sum(lum_img, axis=1) # Sum each row
	width, height = np.shape(lum_img)
	x_proj_hor = np.arange(height)* m
	y_proj_hor = np.arange(width)* m
		
	return x_proj, y_proj, x_proj_hor, y_proj_hor, width, height, m
	
def proj_func_sld_image(lum_img, Screen, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos):
	
	m = 	screen_slector(Screen) # Name is correct !!!
	
	if (sld_h1_pos < sld_h2_pos) and (sld_v1_pos < sld_v2_pos):
		x_proj = np.sum(lum_img[sld_v1_pos:sld_v2_pos, sld_h1_pos:sld_h2_pos], axis=0) # Sum each column
		y_proj = np.sum(lum_img[sld_v1_pos:sld_v2_pos, sld_h1_pos:sld_h2_pos], axis=1) # Sum each row
		width_sld, height_sld = np.shape(lum_img[sld_v1_pos:sld_v2_pos, sld_h1_pos:sld_h2_pos])
		x_proj_hor = (np.arange(height_sld)+sld_h1_pos)* m
		y_proj_hor = (np.arange(width_sld)+sld_v1_pos)* m
	elif (sld_h2_pos < sld_h1_pos) and (sld_v2_pos < sld_v1_pos):
		x_proj = np.sum(lum_img[sld_v2_pos:sld_v1_pos, sld_h2_pos:sld_h1_pos], axis=0) # Sum each column
		y_proj = np.sum(lum_img[sld_v2_pos:sld_v1_pos, sld_h2_pos:sld_h1_pos], axis=1) # Sum each row
		width_sld, height_sld = np.shape(lum_img[sld_v2_pos:sld_v1_pos, sld_h2_pos:sld_h1_pos])
		x_proj_hor = (np.arange(height_sld)+sld_h2_pos)* m
		y_proj_hor = (np.arange(width_sld)+sld_v2_pos)* m
	elif (sld_h1_pos < sld_h2_pos) and (sld_v2_pos < sld_v1_pos):
		x_proj = np.sum(lum_img[sld_v2_pos:sld_v1_pos, sld_h1_pos:sld_h2_pos], axis=0) # Sum each column
		y_proj = np.sum(lum_img[sld_v2_pos:sld_v1_pos, sld_h1_pos:sld_h2_pos], axis=1) # Sum each row
		width_sld, height_sld = np.shape(lum_img[sld_v2_pos:sld_v1_pos, sld_h1_pos:sld_h2_pos])
		x_proj_hor = (np.arange(height_sld)+sld_h1_pos)* m
		y_proj_hor = (np.arange(width_sld)+sld_v2_pos)* m
	elif (sld_h2_pos < sld_h1_pos) and (sld_v1_pos < sld_v2_pos):
		x_proj = np.sum(lum_img[sld_v1_pos:sld_v2_pos, sld_h2_pos:sld_h1_pos], axis=0) # Sum each column
		y_proj = np.sum(lum_img[sld_v1_pos:sld_v2_pos, sld_h2_pos:sld_h1_pos], axis=1) # Sum each row
		width_sld, height_sld = np.shape(lum_img[sld_v1_pos:sld_v2_pos, sld_h2_pos:sld_h1_pos])
		x_proj_hor = (np.arange(height_sld)+sld_h2_pos)* m
		y_proj_hor = (np.arange(width_sld)+sld_v1_pos)* m
	elif (sld_h2_pos == sld_h1_pos) or (sld_v1_pos == sld_v2_pos):
		x_proj = np.sum(lum_img[sld_v1_pos:sld_v2_pos+1, sld_h2_pos:sld_h1_pos+1], axis=0) # Sum each column
		y_proj = np.sum(lum_img[sld_v1_pos:sld_v2_pos+1, sld_h2_pos:sld_h1_pos+1], axis=1) # Sum each row
		width_sld, height_sld = np.shape(lum_img[sld_v1_pos:sld_v2_pos+1, sld_h2_pos:sld_h1_pos+1])
		x_proj_hor = (np.arange(height_sld)+sld_h2_pos)* m
		y_proj_hor = (np.arange(width_sld)+sld_v1_pos)* m
		
	width, height = np.shape(lum_img)
	return x_proj, y_proj, x_proj_hor, y_proj_hor, width_sld, height_sld, width, height, m