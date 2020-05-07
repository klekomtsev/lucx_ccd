#!/usr/bin/env python2.7

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, SIGNAL
from lucx_snapshot import LUCXsnapshot
import time, os, epics, commands
import numpy as np
from ccd_proj_functions import screen_slector

class workThread( QtCore.QThread ):
	def __init__( self, name, parent = None ):
		QtCore.QThread.__init__( self, parent )
		self.name = name
		self.running = False
		self.counter = 0
		self.c = 0
		self.i = 0
		self.k = 0
	
	def run( self ):
		self.running = True
		trigPV 	= 'CAMAC2:S17:CADC6:CH02_MON'
		self.Nshots_str, self.Screen = str(self.name).split(',')
		
		self.Nshots = int(self.Nshots_str)
		
		if self.Screen== 'UVCCD':
			scanPV 	= 'SCR:UV1:IMAGE'
		elif self.Screen == 'UV_LTL':
			scanPV 	= 'SCR:UV2:IMAGE'
		elif self.Screen == 'MS1G':
			scanPV 	= 'SCR:MS1G:IMAGE'
		elif self.Screen == 'MS2G':
			scanPV 	= 'SCR:MS2G:IMAGE'
		elif self.Screen == 'CP1G':
			scanPV 	= 'SCR:CP1G:IMAGE'
		elif self.Screen == 'MS3G':
			scanPV 	= 'SCR:MS3G:IMAGE'
		
		m = screen_slector(self.Screen)
		FilterSts = 0
		FilterSelect = 'Median'
		FilterOrder = 3
		cursor_state = 0
		sld_h1_pos = sld_h2_pos = sld_v1_pos = sld_v2_pos = 0
		
		
		def onChanges(pvname=None, value=None, **kw):
			self.Params = ''
			MM0 = commands.getoutput("caget -t "+scanPV)
			if self.Screen== 'UVCCD':
				mm0, mm1, mm2, mm3 = (commands.getoutput("caget -t "	+" GLSR:POWER:UV:TOGUN_ANG_MON"
																+" GLSR:MIRROR:UV:X_MON"
																+" GLSR:MIRROR:UV:Y_MON"
																+" RFGTB:BM:PD1"
																)).split('\n')
				a1 = np.array(['UV_att', 'UVmirX', 'UVmirY', 'UVPD', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
				a2 = np.array([mm0, mm1, mm2, mm3, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])

			elif self.Screen == 'UV_LTL':
				mm0, mm1, mm2, mm3 = (commands.getoutput("caget -t "	+" GLSR:POWER:UV:TOGUN_ANG_MON"
																+" GLSR:MIRROR:UV:X_MON"
																+" GLSR:MIRROR:UV:Y_MON"
																+" RFGTB:BM:PD1"
																)).split('\n')
				a1 = np.array(['UV_att', 'UVmirX', 'UVmirY', 'UVPD', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
				a2 = np.array([mm0, mm1, mm2, mm3, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
				
			elif self.Screen == 'MS1G':
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
				
			elif self.Screen == 'MS2G':
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
				
			elif self.Screen == 'CP1G':
				mm0, mm1, mm2, mm3, mm4, mm5 = (commands.getoutput("caget -t "	+" LLRF:PHASE:KLY0_MON"
																		+" LLRF:PHASE:KLY1_MON"
																		+" MAGNET:MON:QF4_I_MON"
																		+" MAGNET:MON:QD4_I_MON"
																		+" CAMAC2:S17:CADC6:CH03_MON" # FCT
																		+" BMON:CUR:ICT1S"
																		)).split('\n')
				a1 = np.array(['KLY0ph', 'KLY1ph', 'QF4', 'QD4', 'FCT', 'ICTs', 'SCMAG', 'FSTS', 'FTYPE', 'FORDER', 'CURSTS', 'CURH1', 'CURH2', 'CURV1', 'CURV2'])
				a2 = np.array([mm0, mm1, mm2, mm3, mm4, mm5, m, FilterSts, FilterSelect, FilterOrder, cursor_state, sld_h1_pos, sld_h2_pos, sld_v1_pos, sld_v2_pos])
				
			elif self.Screen == 'MS3G':
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
			
			for i in range(0, len(a1)):
				self.Params += (a1[i] + '\t'+a2[i] + '\n')
			
			self.emit(SIGNAL('data_from_thread(const QString)'),   MM0)
			self.emit(SIGNAL('header_from_thread(const QString)'), self.Params)
			self.i= self.i+1
			if self.i >= self.Nshots and self.Nshots != 1949:
				self.stop()
				self.emit(SIGNAL('get_finished(const QString)'), '')
		
		self.pv1 = epics.PV(trigPV)
		self.pv1.add_callback(onChanges)

	def stop( self ):
		self.pv1.clear_callbacks()
		self.terminate()
		self.wait()
