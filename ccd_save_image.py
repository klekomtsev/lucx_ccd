#!/usr/bin/env python2.7

import numpy as np
import time, os, commands
from astropy.io import fits

def create_folder(dir):
	if not os.path.exists(dir):
		try:
			os.makedirs(dir)
		except OSError as error:
			if error.errno != errno.EEXIST:
				raise
'''
def save_image(startGetcounter, newimg, FilenameToSave, Screen, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos):
	
	filename = "/home/lucxopr/run/data_archive/"+time.strftime("%y_%m_%d")+"/"+time.strftime("%y_%m_%d")+time.strftime("_%H_%M_%S")+"_"+Screen+"_"+FilenameToSave+'_'+str(startGetcounter)+".fit"
	dir, file = os.path.split(filename)
	create_folder(dir)
	
	NameOfFile = file
	NameOfFolder = dir
	
	if Screen== 'UVCCD':
		mm0, mm1, mm2, mm3 = (commands.getoutput("caget -t "	+" GLSR:POWER:UV:TOGUN_ANG_MON"
														+" GLSR:MIRROR:UV:X_MON"
														+" GLSR:MIRROR:UV:Y_MON"
														+" RFGTB:BM:PD1"
														)).split('\n')
		a1 = np.array(['UV_att', 'UVmirX', 'UVmirY', 'UVPD', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_uv_cathode'
		create_folder(dir)

	elif Screen == 'UV_LTL':
		mm0, mm1, mm2, mm3 = (commands.getoutput("caget -t "	+" GLSR:POWER:UV:TOGUN_ANG_MON"
														+" GLSR:MIRROR:UV:X_MON"
														+" GLSR:MIRROR:UV:Y_MON"
														+" RFGTB:BM:PD1"
														)).split('\n')
		a1 = np.array(['UV_att', 'UVmirX', 'UVmirY', 'UVPD', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_uv_ltl'
		create_folder(dir)
		
	elif Screen == 'MS1G':
		mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7 = (commands.getoutput("caget -t "	+" MAGNET:MON:SOL_I_SET_r"
																			+" GLSR:MIRROR:UV:X_MON"
																			+" GLSR:MIRROR:UV:Y_MON"
																			+" MAGNET:MON:ZV2_I_MON"
																			+" MAGNET:MON:ZH2_I_MON"
																			+" LLRF:PHASE:KLY0_MON"
																			+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																			+" BMON:CUR:ICT1S"
																			)).split('\n')
		a1 = np.array(['SOL', 'UVmirX', 'UVmirY', 'ZV2', 'ZH2', 'KLY0ph', 'FCT', 'ICTs', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/01_ms1g'
		create_folder(dir)
		
	elif Screen == 'MS2G':
		mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7 = (commands.getoutput("caget -t "	+" MAGNET:MON:SOL_I_SET_r"
																			+" GLSR:MIRROR:UV:X_MON"
																			+" GLSR:MIRROR:UV:Y_MON"
																			+" MAGNET:MON:ZV2_I_MON"
																			+" MAGNET:MON:ZH2_I_MON"
																			+" LLRF:PHASE:KLY0_MON"
																			+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																			+" BMON:CUR:ICT1S"
																			)).split('\n')
		a1 = np.array(['SOL', 'UVmirX', 'UVmirY','ZV2', 'ZH2', 'KLY0ph', 'FCT', 'ICTs', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/02_ms2g'
		create_folder(dir)
		
	elif Screen == 'CP1G':
		mm0, mm1, mm2, mm3, mm4, mm5 = (commands.getoutput("caget -t "	+" LLRF:PHASE:KLY0_MON"
																+" LLRF:PHASE:KLY1_MON"
																+" MAGNET:MON:QF4_I_MON"
																+" MAGNET:MON:QD4_I_MON"
																+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																+" BMON:CUR:ICT1S"
																)).split('\n')
		a1 = np.array(['KLY0ph', 'KLY1ph', 'QF4', 'QD4', 'FCT', 'ICTs', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/03_cp1g'
		create_folder(dir)
		
	elif Screen == 'MS3G':
		mm0, mm1, mm2, mm3, mm4, mm5, mm6 = (commands.getoutput("caget -t "	+" LLRF:PHASE:KLY0_MON"
																	+" LLRF:PHASE:KLY1_MON"
																	+" MAGNET:MON:BH1_I_MON"
																	+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																	+" BMON:CUR:ICT1S"
																	+" thz:buncher:m1:pos"
																	+" thz:buncher:m2:pos"
																	)).split('\n')
		a1 = np.array(['KLY0ph', 'KLY1ph', 'BH1', 'FCT', 'ICTs', 'bunM1', 'bunM2', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, mm6, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/04_ms3g'
		create_folder(dir)
	
	imageHeader =  fits.Header()
	hdu = fits.CompImageHDU(newimg, imageHeader)
	for i in range(0, len(a1)):
		hdu.header.append((a1[i], a2[i], 'alar'), end=True) # Adding a CARD to the HDU header end. Card consist of: name, value, comment
	hdu.writeto(dir + '/'+ file)
	return NameOfFile, NameOfFolder
	
def save_back(startGetcounter, newimg, FilenameToSave, Screen, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos):
	
	filename = "/home/lucxopr/run/data_archive/"+time.strftime("%y_%m_%d")+"/"+time.strftime("%y_%m_%d")+time.strftime("_%H_%M_%S")+"_"+Screen+"_"+FilenameToSave+'_'+str(startGetcounter)+".fit"
	dir, file = os.path.split(filename)
	create_folder(dir)
	
	NameOfFile = file
	NameOfFolder = dir + '/00_dark'
	
	if Screen== 'UVCCD':
		mm0, mm1, mm2, mm3 = (commands.getoutput("caget -t "	+" GLSR:POWER:UV:TOGUN_ANG_MON"
														+" GLSR:MIRROR:UV:X_MON"
														+" GLSR:MIRROR:UV:Y_MON"
														+" RFGTB:BM:PD1"
														)).split('\n')
		a1 = np.array(['UV_att', 'UVmirX', 'UVmirY', 'UVPD', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_dark'
		create_folder(dir)

	elif Screen == 'UV_LTL':
		mm0, mm1, mm2, mm3 = (commands.getoutput("caget -t "	+" GLSR:POWER:UV:TOGUN_ANG_MON"
														+" GLSR:MIRROR:UV:X_MON"
														+" GLSR:MIRROR:UV:Y_MON"
														+" RFGTB:BM:PD1"
														)).split('\n')
		a1 = np.array(['UV_att', 'UVmirX', 'UVmirY', 'UVPD', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_dark'
		create_folder(dir)
		
	elif Screen == 'MS1G':
		mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7 = (commands.getoutput("caget -t "	+" MAGNET:MON:SOL_I_SET_r"
																			+" GLSR:MIRROR:UV:X_MON"
																			+" GLSR:MIRROR:UV:Y_MON"
																			+" MAGNET:MON:ZV2_I_MON"
																			+" MAGNET:MON:ZH2_I_MON"
																			+" LLRF:PHASE:KLY0_MON"
																			+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																			+" BMON:CUR:ICT1S"
																			)).split('\n')
		a1 = np.array(['SOL', 'UVmirX', 'UVmirY', 'ZV2', 'ZH2', 'KLY0ph', 'FCT', 'ICTs', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_dark'
		create_folder(dir)
		
	elif Screen == 'MS2G':
		mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7 = (commands.getoutput("caget -t "	+" MAGNET:MON:SOL_I_SET_r"
																			+" GLSR:MIRROR:UV:X_MON"
																			+" GLSR:MIRROR:UV:Y_MON"
																			+" MAGNET:MON:ZV2_I_MON"
																			+" MAGNET:MON:ZH2_I_MON"
																			+" LLRF:PHASE:KLY0_MON"
																			+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																			+" BMON:CUR:ICT1S"
																			)).split('\n')
		a1 = np.array(['SOL', 'UVmirX', 'UVmirY','ZV2', 'ZH2', 'KLY0ph', 'FCT', 'ICTs', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, mm6, mm7, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_dark'
		create_folder(dir)
		
	elif Screen == 'CP1G':
		mm0, mm1, mm2, mm3, mm4, mm5 = (commands.getoutput("caget -t "	+" LLRF:PHASE:KLY0_MON"
																+" LLRF:PHASE:KLY1_MON"
																+" MAGNET:MON:QF4_I_MON"
																+" MAGNET:MON:QD4_I_MON"
																+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																+" BMON:CUR:ICT1S"
																)).split('\n')
		a1 = np.array(['KLY0ph', 'KLY1ph', 'QF4', 'QD4', 'FCT', 'ICTs', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_dark'
		create_folder(dir)
		
	elif Screen == 'MS3G':
		mm0, mm1, mm2, mm3, mm4, mm5, mm6 = (commands.getoutput("caget -t "	+" LLRF:PHASE:KLY0_MON"
																	+" LLRF:PHASE:KLY1_MON"
																	+" MAGNET:MON:BH1_I_MON"
																	+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																	+" BMON:CUR:ICT1S"
																	+" thz:buncher:m1:pos"
																	+" thz:buncher:m2:pos"
																	)).split('\n')
		a1 = np.array(['KLY0ph', 'KLY1ph', 'BH1', 'FCT', 'ICTs', 'bunM1', 'bunM2', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
		a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, mm6, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
		dir = dir + '/00_dark'
		create_folder(dir)
	
	imageHeader =  fits.Header()
	hdu = fits.CompImageHDU(newimg, imageHeader)
	for i in range(0, len(a1)):
		hdu.header.append((a1[i], a2[i], 'alar'), end=True) # Adding a CARD to the HDU header end. Card consist of: name, value, comment
	hdu.writeto(dir + '/'+ file)
	
	return NameOfFile, NameOfFolder
'''	
