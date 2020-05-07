#!/usr/bin/env python2.7

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import glob
from mpl_toolkits.axes_grid1 import make_axes_locatable

import numpy as np
from scipy.signal import argrelmax
from scipy import ndimage
from scipy.signal import argrelextrema
import sys, commands, time, os

#from ccd_low_level import workThread
from ccd_proj_functions import proj_func_full_image, proj_func_sld_image
from ccd_gauss_fit_functions import gauss_fit_function, skew_gauss_fit_function, two_gauss_fit_function, two_skew_gauss_fit_function, two_gauss_fit_function_FixSigma, fit_func, skew_fit_func, two_fit_func, two_skew_fit_func, two_fit_func_fixSigma, four_fit_func, four_gauss_fit_function
from ccd_back_n_filter import BF_proc
from ccd_save_image import create_folder
from ccd_open_image import imageOpener

class MainWindow(QMainWindow):
	def __init__(self, parent=None, *args):
		super(MainWindow, self).__init__(parent)
		#self.setStyleSheet("background-color: #ececec"); 
		
		self.scanner = Scanner()
		
		""" MENU BAR SETUP """
		""" FILE MENU """
		self.menuFile = self.menuBar().addMenu("&File")
		self.actionSaveAs = QAction("&Save As", self)
		self.connect(self.actionSaveAs, SIGNAL("triggered()"), self.saveas) 
		self.actionExit= QAction("&Exit", self)
		self.connect(self.actionExit, SIGNAL("triggered()"), self.close)   
		self.menuFile.addActions([self.actionSaveAs, self.actionExit])
		'''
		""" VIEW MENU """
		self.menuView = self.menuBar().addMenu("&View")
		self.actionViewAna = QAction("&Analysis", self)
		#self.connect(self.actionViewAna, SIGNAL("triggered()"), self.scanner.view_analysis) 
		self.actionViewAqui= QAction("&Aquisition", self)
		#self.connect(self.actionViewAqui, SIGNAL("triggered()"), self.scanner.view_aquisition)   
		self.menuView.addActions([self.actionViewAna, self.actionViewAqui])
		'''
		""" HELP MENU """
		self.menuHelp = self.menuBar().addMenu("&Help")
		self.actionAbout = QAction("&About", self)
		self.connect(self.actionAbout, SIGNAL("triggered()"), self.about)
		self.menuHelp.addActions([self.actionAbout])
		
		""" CENTRAL WIDGET """ 
		self.form = Scanner()
		self.setCentralWidget(self.form)
		
	def saveas(self) :
		fname = unicode(QFileDialog.getSaveFileName(self, "Save as..."))
		""" Do something with data """

	def about(self) :
		QMessageBox.about(self, "About Function Evaluator", "This is my help message.")

class Scanner(QDialog):
	st = 0
	stop = 1000
	step = 1
	nshots = 5
	i = 0
	
	def __init__(self, parent=None):
		super(Scanner, self).__init__(parent)
		self.Nshots = '2'
		self.Screen = 'UVCCD'
		
		self.plot = MatplotlibCanvas()

		self.toolbar = NavigationToolbar(self.plot, self)
		#self.toolbar.hide()
	
		self.button1 = QPushButton('Update')
		self.button1.setFixedWidth(70)
		self.button1.clicked.connect(self.plot.update_figure)
		self.button3 = QComboBox(self)
		self.button3.addItem("Save Fit")
		self.button3.addItem("PrintScr")
		#QPushButton('Save')
		#self.button3.setFixedWidth(70)
		self.button3.activated[str].connect(self.save_img)
		
		self.buttonMonitor = QPushButton('Monitor')
		self.buttonMonitor.setFixedWidth(70)
		#self.buttonMonitor.clicked.connect(self.startMonitor)
		self.buttonStop = QPushButton('Stop')
		self.buttonStop.setFixedWidth(70)
		#self.buttonStop.clicked.connect(self.stopMonitor)
		self.buttonGet = QPushButton('Get')
		self.buttonGet.setFixedWidth(70)
		#self.buttonGet.clicked.connect(self.startGet)
		#self.buttonGet.clicked.connect(self.plot.startGetcounter)
		self.buttonGetBack = QPushButton('GetBack')
		self.buttonGetBack.setFixedWidth(70)
		#self.buttonGetBack.clicked.connect(self.startGetBack)
		self.buttonGetBack.clicked.connect(self.plot.startGetcounter)
		
		self.LineEdit0 = QLineEdit(self)
		QObject.connect(self.plot, SIGNAL('foldername(const QString)'),self.LineEdit0.setText)
		
		self.comboPath = QComboBox(self)
		self.comboPath.addItem("SetFolder")
		self.comboPath.addItem("SetFile")
		self.comboPath.setFixedWidth(100)
		self.comboPath.activated[str].connect(self.selectPath)
		
		self.buttonRev = QPushButton('<')
		self.buttonRev.setFixedWidth(40)
		self.buttonRev.clicked.connect(self.plot.buttonRev)
		self.buttonFor = QPushButton('>')
		self.buttonFor.setFixedWidth(40)
		self.buttonFor.clicked.connect(self.plot.buttonFor)
		
		self.button1by1 = QPushButton('OneBy1')
		self.button1by1.setFixedWidth(70)
		self.button1by1.clicked.connect(self.plot.OneBy1)
		self.buttonFileClose = QPushButton('X')
		self.buttonFileClose.setFixedWidth(10)
		self.buttonFileClose.clicked.connect(self.plot.buttonFileClose)
		
		self.LabelFile = QLabel('')
		self.LabelFile.setMinimumWidth(600)
		self.LabelFile.setWordWrap(True)
		QObject.connect(self.plot, SIGNAL('filename(const QString)'),self.LabelFile.setText)
		
		self.checkFilter = QCheckBox('Filter')
		QObject.connect(self.checkFilter, SIGNAL('stateChanged(int)'), self.plot.Filter)
		self.comboFilterType = QComboBox(self)
		self.comboFilterType.addItem("Uniform")
		self.comboFilterType.addItem("Gaussian")
		self.comboFilterType.addItem("Median")
		self.comboFilterType.addItem("Denoise TV")
		self.comboFilterType.addItem("Bilateral")
		self.comboFilterType.setFixedWidth(80)
		self.comboFilterType.activated[str].connect(self.plot.selectFilter)
		self.LineEdit0b = QLineEdit(self)
		self.LineEdit0b.setText('3')
		self.LineEdit0b.setFixedWidth(40)
		QObject.connect(self.LineEdit0b,SIGNAL('textChanged(const QString)'),self.plot.FilterOrder)
		
		
		self.LineEdit0a = QLineEdit(self)
		self.LineEdit0a.setText('')
		self.LineEdit0a.setFixedWidth(200)
		QObject.connect(self.LineEdit0a,SIGNAL('textChanged(const QString)'),self.plot.FilenameToSave)
		self.plot.SetDefaults()
		
		self.LabelBack = QLabel('')
		self.LabelBack.setMinimumWidth(200)
		self.LabelBack.setWordWrap(True)
		QObject.connect(self.plot, SIGNAL('backname(const QString)'),self.LabelBack.setText)
		
		self.buttonBack = QPushButton('Set Back')
		self.buttonBack.setFixedWidth(70)
		self.buttonBack.clicked.connect(self.setBack)
		
		self.buttonProcAll = QPushButton('Proc. all')
		self.buttonProcAll.setFixedWidth(70)
		self.buttonProcAll.clicked.connect(self.plot.ProcAll)
		
		self.editor = QLabel('')#QTextEdit()
		#self.editor.setMinimumHeight(300)
		QObject.connect(self.plot, SIGNAL('header_from_fit_file(const QString)'),self.editor.setText)
		
		self.FitLabel_x = QLabel('Horizontal fit:\n ver. offset =\n Slope =\n Amplitude =\n hor. offset =\n Sigma =')
		self.FitLabel_x.setFixedWidth(200)
		self.FitLabel_y = QLabel('Vertical fit:\n ver. offset =\n Slope =\n Amplitude =\n hor. offset =\n Sigma =')
		self.FitLabel_y.setFixedWidth(200)
		QObject.connect(self.plot, SIGNAL('fit_string_x(const QString)'),self.FitLabel_x.setText)
		QObject.connect(self.plot, SIGNAL('fit_string_y(const QString)'),self.FitLabel_y.setText)
		
		self.LineEdit2 = QLineEdit(self)
		self.LineEdit2.setText('2')
		self.LineEdit2.setFixedWidth(40)
		QObject.connect(self.LineEdit2,SIGNAL('textChanged(const QString)'),self.changeNshots)
		
		self.LineEdit1 = QLineEdit(self)
		self.LineEdit1.setText('256')
		self.LineEdit1.setFixedWidth(40)
		QObject.connect(self.LineEdit1,SIGNAL('textChanged(const QString)'),self.plot.getValue_Intensity_sld)
		QObject.connect(self.LineEdit1,SIGNAL('textChanged(const QString)'),self.changeSlider)
		
		self.sld = QSlider(Qt.Horizontal)
		self.sld.setFocusPolicy(Qt.NoFocus)
		self.sld.setGeometry(30, 40, 100, 30)
		self.sld.setRange(1,256)
		self.sld.setValue(256)
		QObject.connect(self.sld, SIGNAL('valueChanged(int)'), self.plot.getValue_Intensity_sld)
		QObject.connect(self.sld, SIGNAL('valueChanged(int)'), self.changeText)
		
		self.check_auto_scale = QCheckBox('Auto')
		self.check_auto_scale.setChecked(True)
		QObject.connect(self.check_auto_scale, SIGNAL('stateChanged(int)'), self.plot.AutoScale)
		
		self.comboScreen = QComboBox(self)
		self.comboScreen.addItem("UVCCD")
		self.comboScreen.addItem("UVLTL")
		self.comboScreen.addItem("MS1G")
		self.comboScreen.addItem("MS2G")
		self.comboScreen.addItem("CP1G")
		self.comboScreen.addItem("MS3G")
		self.comboScreen.addItem("Pixel")
		self.comboScreen.addItem("AstraX")
		self.comboScreen.addItem("AstraZ")
		self.comboScreen.setFixedWidth(70)
		self.comboScreen.activated[str].connect(self.selectScreen)
		self.comboScreen.activated[str].connect(self.plot.selectScreen)
		
		self.buttonGetStat = QPushButton('GetStat')
		self.buttonGetStat.setFixedWidth(70)
		#self.buttonGetStat.clicked.connect(self.startGetStat)
		self.buttonGetStat.clicked.connect(self.plot.startGetcounter)
		
		self.check1 = QCheckBox('Fit X')
		QObject.connect(self.check1, SIGNAL('stateChanged(int)'), self.plot.FitX)
		QObject.connect(self.check1, SIGNAL('stateChanged(int)'), self.FitX)
		self.check2 = QCheckBox('Fit Y')
		QObject.connect(self.check2, SIGNAL('stateChanged(int)'), self.plot.FitY)
		QObject.connect(self.check2, SIGNAL('stateChanged(int)'), self.FitY)
		self.check3 = QCheckBox('Fit both')
		QObject.connect(self.check3, SIGNAL('stateChanged(int)'), self.plot.FitXY)
		QObject.connect(self.check3, SIGNAL('stateChanged(int)'), self.FitXY)
		self.check4 = QCheckBox('Fit 2D')
		QObject.connect(self.check4, SIGNAL('stateChanged(int)'), self.Fit2D)
		self.check_curr = QCheckBox('Cursors')
		QObject.connect(self.check_curr, SIGNAL('stateChanged(int)'), self.plot.Cursors)
		self.check_back = QCheckBox('Back Sbs')
		self.check_back.setChecked(True)
		QObject.connect(self.check_back, SIGNAL('stateChanged(int)'), self.plot.BackSbs)
		
		self.comboFitX = QComboBox(self)
		self.comboFitX.addItem("1 Gauss")
		self.comboFitX.addItem("Sk Gauss")
		self.comboFitX.addItem("2 Gauss")
		self.comboFitX.addItem("2 Sk Gauss")
		self.comboFitX.addItem("2 G_Fix")
		self.comboFitX.addItem("4 Gauss")
		self.comboFitX.setFixedWidth(80)
		self.comboFitX.activated[str].connect(self.plot.selectFitX)
		
		self.LineEdit3 = QLineEdit(self)
		self.LineEdit3.setText('1100')
		self.LineEdit3.setFixedWidth(40)
		QObject.connect(self.LineEdit3,SIGNAL('textChanged(const QString)'),self.plot.FixSigma)
		self.LabelFixSigma = QLabel('FixSigma')
		#self.LabelBack.setFixedWidth(20)
		
		# ROI sliders
		self.sld_h1 = QSlider(Qt.Horizontal)
		self.sld_h1.setFocusPolicy(Qt.NoFocus)
		#self.sld_h1.setGeometry(30, 40, 100, 30)
		self.sld_h1.setRange(1,640)
		self.sld_h1.setValue(100)
		QObject.connect(self.sld_h1, SIGNAL('valueChanged(int)'), self.plot.getValueSLD_h1)
		QObject.connect(self.sld_h1, SIGNAL('sliderReleased()'), self.plot.Updater)
		self.sld_h2 = QSlider(Qt.Horizontal)
		self.sld_h2.setFocusPolicy(Qt.NoFocus)
		#self.sld_h2.setGeometry(30, 40, 100, 30)
		self.sld_h2.setRange(1,640)
		self.sld_h2.setValue(200)
		QObject.connect(self.sld_h2, SIGNAL('valueChanged(int)'), self.plot.getValueSLD_h2)
		QObject.connect(self.sld_h2, SIGNAL('sliderReleased()'), self.plot.Updater)
		
		self.sld_v1 = QSlider(Qt.Vertical)
		self.sld_v1.setFocusPolicy(Qt.NoFocus)
		self.sld_v1.setInvertedAppearance(True)
		#self.sld_v1.setGeometry(30, 40, 100, 30)
		self.sld_v1.setRange(1,480)
		self.sld_v1.setValue(100)
		QObject.connect(self.sld_v1, SIGNAL('valueChanged(int)'), self.plot.getValueSLD_v1)
		QObject.connect(self.sld_v1, SIGNAL('sliderReleased()'), self.plot.Updater)
		self.sld_v2 = QSlider(Qt.Vertical)
		self.sld_v2.setFocusPolicy(Qt.NoFocus)
		self.sld_v2.setInvertedAppearance(True)
		#self.sld_v2.setGeometry(30, 40, 100, 30)
		self.sld_v2.setRange(1,480)
		self.sld_v2.setValue(200)
		QObject.connect(self.sld_v2, SIGNAL('valueChanged(int)'), self.plot.getValueSLD_v2)
		QObject.connect(self.sld_v2, SIGNAL('sliderReleased()'), self.plot.Updater)
		'''
		self.tabs = QTabWidget(self)
		self.widget = QWidget(self)
		self.tab2	= QWidget(self)
		self.tabs.addTab(self.widget,"Tab 1")
		self.tabs.addTab(self.tab2,"Tab 2")
		'''
		# set the layout
		hbox0 = QHBoxLayout()
		hbox0a = QHBoxLayout()
		hbox0b = QHBoxLayout()
		hbox1 = QHBoxLayout()
		hbox2 = QHBoxLayout()
		hbox3 = QHBoxLayout()
		hbox4 = QHBoxLayout()
		hbox5 = QHBoxLayout()
		vbox1 = QVBoxLayout()
		vbox2 = QVBoxLayout()
		vbox3 = QVBoxLayout()
		vbox4 = QVBoxLayout()
			
		vbox1.addLayout(hbox0)
		hbox0.addWidget(self.LineEdit0)
		hbox0.addWidget(self.comboPath)
		hbox0.addWidget(self.buttonRev)
		hbox0.addWidget(self.buttonFor)
		hbox0.addWidget(self.button1by1)
		hbox0.addWidget(self.buttonFileClose)
		vbox1.addLayout(hbox0a)
		hbox0a.addWidget(self.LabelFile)
		hbox0a.addWidget(self.LabelFixSigma)
		hbox0a.addWidget(self.LineEdit3)
		hbox0a.addWidget(self.checkFilter)
		hbox0a.addWidget(self.comboFilterType)
		hbox0a.addWidget(self.LineEdit0b)
		vbox1.addLayout(hbox0b)
		hbox0b.addWidget(self.LineEdit0a)
		hbox0b.addWidget(self.buttonGetStat)
		hbox0b.addWidget(self.LabelBack)
		hbox0b.addWidget(self.buttonBack)
		hbox0b.addWidget(self.buttonProcAll)
		vbox1.addLayout(hbox1)
		hbox1.addWidget(self.buttonGet)
		hbox1.addWidget(self.buttonMonitor)
		hbox1.addWidget(self.buttonStop)
		hbox1.addWidget(self.buttonGetBack)
		hbox1.addWidget(self.LineEdit2)
		hbox1.addWidget(self.comboScreen)
		hbox1.addWidget(self.check1)
		hbox1.addWidget(self.comboFitX)
		hbox1.addWidget(self.check2)
		hbox1.addWidget(self.check3)
		hbox1.addWidget(self.check4)
		hbox1.addWidget(self.check_curr)
		hbox1.addWidget(self.check_back)
		
		vbox1.addLayout(hbox3)
		hbox3.addLayout(vbox2)
		vbox2.addLayout(hbox2)
		hbox2.addWidget(self.sld_h1)
		hbox2.addWidget(self.sld_h2)
		vbox2.addWidget(self.plot)
		vbox2.addWidget(self.toolbar)
		
		hbox3.addLayout(vbox3)
		vbox3.addWidget(self.sld_v1)
		vbox3.addWidget(self.sld_v2)
		
		hbox3.addLayout(vbox4)
		vbox4.addWidget(self.FitLabel_x)
		vbox4.addWidget(self.FitLabel_y)
		vbox4.addWidget(self.editor)
	
		vbox1.addLayout(hbox4)
		hbox4.addWidget(self.button1)
		hbox4.addWidget(self.button3)
		hbox4.addWidget(self.sld)
		hbox4.addWidget(self.LineEdit1)
		hbox4.addWidget(self.check_auto_scale)

		hbox1.setAlignment(Qt.AlignLeft)
		hbox2.setAlignment(Qt.AlignLeft)
		'''
		vbox1.addWidget(self.tabs)
		self.widget.setLayout(hbox4)
		hbox4.addWidget(self.button1)
		hbox4.addWidget(self.button3)
		hbox4.addWidget(self.sld)
		hbox4.addWidget(self.LineEdit1)
		hbox4.addWidget(self.check_auto_scale)
		'''
		self.setLayout(vbox1)

	def selectPath(self, text):
		if text == 'SetFolder':
			ImgFolder = QFileDialog.getExistingDirectory(self, "Open Image Folder","/home/lucxopr/run/data_archive")
			self.LineEdit0.setText(ImgFolder)
			results = []
			results += [each for each in os.listdir(ImgFolder) if each.endswith('.ppm') or each.endswith('.fit') or each.endswith('.dat') or each.endswith('.astra')]
			self.plot.ImgFolder(ImgFolder, results)
		elif text == 'SetFile':
			ImgFile = QFileDialog.getOpenFileName(self, "Open Image File","/home/lucxopr/run/data_archive","Images (*.ppm *.fit *.fits *.dat *.astra)")
			self.LineEdit0.setText(ImgFile)
			self.plot.ImgFile(ImgFile)
	def save_img(self, text):
		if text == 'Save Fit':
			self.LineEdit0a.setText('save')
			self.plot.update_figure('0')
			self.LineEdit0a.setText('')
		elif text == 'PrintScr':
			self.plot.save()
			
	def setBack(self):
		BackTxt = QFileDialog.getOpenFileName(self, "Open Image background File","/home/lucxopr/run","Images (*.ppm *.fit *.fits *.dat)")
		self.LabelBack.setText(BackTxt)
		self.plot.BackFile(BackTxt)
	def selectScreen(self, text):
		self.Screen = text
	def changeText(self, value):
		self.LineEdit1.setText(str(value))
	def changeSlider(self, value):
		if value >= 1:
			self.sld.setValue(int(value))
	def changeNshots(self, value):
		if value >= 1:
			self.Nshots = str(value)
	def FitX(self):
		if self.check1.isChecked():
			self.check3.setChecked(False)
			self.check4.setChecked(False)
	def FitY(self):
		if self.check2.isChecked():
			self.check3.setChecked(False)
			self.check4.setChecked(False)
	def FitXY(self):
		if self.check3.isChecked():
			self.check1.setChecked(False)
			self.check2.setChecked(False)
			self.check4.setChecked(False)
	def Fit2D(self):
		if self.check4.isChecked():
			self.check1.setChecked(False)
			self.check2.setChecked(False)
			self.check3.setChecked(False)
'''
	def startMonitor(self):
		self.threadMon = workThread('1949'+','+ self.Screen) # just any number for infinite loop
		#QObject.connect( self.threadMon, SIGNAL( "runStatus(PyQt_PyObject)" ), self.editor.append )
		#QObject.connect( self.threadMon, SIGNAL( "thread_sts(const QString)" ), self.editor.append )
		QObject.connect( self.threadMon, SIGNAL( "data_from_thread(const QString)" ), self.plot.figure_data )
		QObject.connect( self.threadMon, SIGNAL( "header_from_thread(const QString)" ), self.editor.setText )
		self.threadMon.start()
		self.buttonMonitor.setEnabled(False)
		self.buttonGet.setEnabled(False)
		self.buttonGetBack.setEnabled(False)

	def startGet(self):
		self.threadMon = workThread(self.Nshots+','+ self.Screen)
		#QObject.connect( self.threadMon, SIGNAL( "runStatus(PyQt_PyObject)" ), self.editor.append)
		#QObject.connect( self.threadMon, SIGNAL( "thread_sts(const QString)" ), self.editor.append)
		QObject.connect( self.threadMon, SIGNAL( "get_finished(const QString)" ), self.stopMonitor)
		QObject.connect( self.threadMon, SIGNAL( "data_from_thread(const QString)" ), self.plot.figure_data)
		QObject.connect( self.threadMon, SIGNAL( "header_from_thread(const QString)" ), self.editor.setText )
		self.threadMon.start()
		self.buttonMonitor.setEnabled(False)
		self.buttonGet.setEnabled(False)
		self.buttonGetBack.setEnabled(False)
		
	def startGetBack(self):
		self.threadMon = workThread('5'+','+ self.Screen)
		#QObject.connect( self.threadMon, SIGNAL( "runStatus(PyQt_PyObject)" ), self.editor.append )
		#QObject.connect( self.threadMon, SIGNAL( "thread_sts(const QString)" ), self.editor.append )
		QObject.connect( self.threadMon, SIGNAL( "get_finished(const QString)" ), self.stopMonitor)
		QObject.connect( self.threadMon, SIGNAL( "data_from_thread(const QString)" ), self.plot.background_data)
		QObject.connect( self.threadMon, SIGNAL( "header_from_thread(const QString)" ), self.editor.setText )
		self.threadMon.start()
		self.buttonMonitor.setEnabled(False)
		self.buttonGet.setEnabled(False)
		self.buttonGetBack.setEnabled(False)

	def startGetStat(self):
		
		self.threadMon = workThread('5'+','+ self.Screen)
		QObject.connect( self.threadMon, SIGNAL( "runStatus(PyQt_PyObject)" ), self.editor.append )
		QObject.connect( self.threadMon, SIGNAL( "thread_sts(const QString)" ), self.editor.append )
		QObject.connect( self.threadMon, SIGNAL( "get_finished(const QString)" ), self.stopMonitor)
		QObject.connect( self.threadMon, SIGNAL( "data_from_thread(const QString)" ), self.plot.background_data)
		self.threadMon.start()
		self.buttonMonitor.setEnabled(False)
		self.buttonGet.setEnabled(False)
		self.buttonGetBack.setEnabled(False)
		
	def stopMonitor(self):
		self.threadMon.stop()
		self.buttonMonitor.setEnabled(True)
		self.buttonGet.setEnabled(True)
		self.buttonGetBack.setEnabled(True)
		self.LineEdit0a.setText('')
'''
class MatplotlibCanvas(FigureCanvas) :
	
	fit_string_x = pyqtSignal(str)
	fit_string_y = pyqtSignal(str)
	filename = pyqtSignal(str)
	foldername = pyqtSignal(str)
	backname = pyqtSignal(str)
	header_from_fit_file = pyqtSignal(str)
	
	def __init__(self, parent=None):#, width=5, height=4, dpi=100) :
		self.fig = plt.figure()#figsize=(width, height), dpi=dpi)
		self.fig.patch.set_facecolor('#ececec')
		self.axes = self.fig.add_subplot(111)
		
		divider = make_axes_locatable(self.axes)
		
		self.proj_x = divider.append_axes("top", 1.2, pad=0.1)#, sharex=self.axes)
		self.proj_y = divider.append_axes("right", 1.2, pad=0.1)#, sharey=self.axes)
		
		self.proj_x.xaxis.tick_top()
		self.proj_x.xaxis.set_ticks_position('both')
		self.proj_x.xaxis.set_label_position('top')
		
		self.proj_y.yaxis.tick_right()
		self.proj_y.yaxis.set_ticks_position('both')
		self.proj_y.yaxis.set_label_position('right')
		
		self.fig.set_tight_layout({"w_pad":0.0})
		self.compute_initial_figure()
		FigureCanvas.__init__(self, self.fig)
		# WHY do I need this ????? 
		self.setParent(parent)
		# ??????
		FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.scale = 256
		self.sld_h1_pos = 100
		self.sld_h2_pos = 200
		self.sld_v1_pos = 100
		self.sld_v2_pos = 200
		self.cursor_state = 0
		self.back_sbs = 2
		self.autoscale = 2
		self.FilterSts = 0
		self.fix_sigma = 1100
		self.FilterSelect = 'Uniform'
		self.backimg = np.zeros((480, 640), dtype=np.float)
		self.filelist = []
		
		self.Screen = 'UVCCD'
		self.selectFit_X = '1 Gauss'
		
	def compute_initial_figure(self):
		self.gap_hor = abs(Scanner.stop - Scanner.st)/10
		self.axes.set_xlim(Scanner.st-self.gap_hor, Scanner.stop+self.gap_hor)
		#self.plt_names('Name')
		#self.axes.set_title(self.plt_title, fontsize=12)
		#self.axes.set_ylabel(self.ylabel)
		#plt.setp(self.proj_x.get_xticklabels() + self.proj_y.get_yticklabels(), visible=False)
		plt.setp(self.proj_x.get_yticklabels() + self.proj_y.get_xticklabels() + self.proj_x.get_xticklabels() + self.proj_y.get_yticklabels(), fontsize=6)
		plt.setp(self.proj_y.get_xticklabels(), rotation='vertical')
		self.A = []
		self.xa = [] 
		self.ya = []
		self.st_x = []
		self.st_y = []
		peaks = [0,0,0,0]
		self.ymin = 0
		self.ymax = 1
		self.gap_ver = 0.1
		self.OneBy1_iter = 0
				
	def figure_data(self,sigstr):
		self.newimg = np.reshape(map(float, str(sigstr).split(' '))[1:], (480,640))
		self.update_figure('0')
	
	def background_data(self,sigstr):
		self.backimg = np.reshape(map(float, str(sigstr).split(' '))[1:], (480,640))
		self.update_figure('0')
		
	def update_figure(self,save, **kwargs):
		self.axes.clear()
		self.proj_x.clear()
		self.proj_y.clear()
			
		#plt.setp(self.proj_x.get_xticklabels() + self.proj_y.get_yticklabels(), visible=False)
		plt.setp(self.proj_x.get_yticklabels() + self.proj_y.get_xticklabels() + self.proj_x.get_xticklabels() + self.proj_y.get_yticklabels(), fontsize=6)
		plt.setp(self.proj_y.get_xticklabels(), rotation='vertical')
		
		# # # Subst Background and apply Filtering
		self.ImageFinal = BF_proc(self.newimg, self.backimg, self.FilterSts, self.FilterOrder, self.FilterSelect, self.back_sbs)
			
		# # # Apply Auto scale
		if self.autoscale == 2:
			self.axes.imshow(self.ImageFinal,cmap='jet', vmin=0, vmax=np.amax(self.ImageFinal)) # interpolation="gaussian",
		else: 
			self.axes.imshow(self.ImageFinal,cmap='jet', vmin=0, vmax=self.scale) # , interpolation="gaussian"
		
		# # # Apply Cursors
		if self.cursor_state == 2:
			self.x_proj, self.y_proj, self.x_proj_hor, self.y_proj_hor, width_sld, height_sld, width, height, self.m = proj_func_sld_image(self.ImageFinal, self.Screen, self.sld_h1_pos, self.sld_h2_pos, self.sld_v1_pos, self.sld_v2_pos)
			
			self.x_proj=self.x_proj/self.x_proj.max() # NORMALIZATION: Horizontal projection, vertical axis
			
			x_proj_st = np.zeros(height_sld)
			y_proj_st = np.zeros(width_sld)
			self.axes.axvline(x=self.sld_h1_pos,ymin=0,ymax=width,c="blue",linewidth=1)
			self.axes.axvline(x=self.sld_h2_pos,ymin=0,ymax=width,c="blue",linewidth=1)
			self.axes.axhline(y=self.sld_v1_pos,xmin=0,xmax=height,c="blue",linewidth=1)
			self.axes.axhline(y=self.sld_v2_pos,xmin=0,xmax=height,c="blue",linewidth=1)
			
			self.proj_x.errorbar(self.x_proj_hor , self.x_proj, xerr=x_proj_st, fmt='-k.', zorder=1)
			self.proj_y.errorbar(self.y_proj, self.y_proj_hor, xerr=y_proj_st, fmt='-k.', zorder=1)
			self.proj_x.set_xlim(self.sld_h1_pos*self.m, self.sld_h2_pos*self.m)
			self.proj_y.set_ylim(self.sld_v1_pos*self.m, self.sld_v2_pos*self.m)
			
			#print self.sld_v1_pos, self.sld_v2_pos

		else:
			self.x_proj, self.y_proj, self.x_proj_hor, self.y_proj_hor, width, height, self.m = proj_func_full_image(self.ImageFinal, self.Screen)
			
			self.x_proj=self.x_proj/self.x_proj.max() # NORMALIZATION: Horizontal projection, vertical axis
			
			x_proj_st = np.zeros(height)
			y_proj_st = np.zeros(width)
			
			self.proj_x.errorbar(self.x_proj_hor , self.x_proj, xerr=x_proj_st, fmt='-k.', zorder=1)
			self.proj_y.errorbar(self.y_proj, self.y_proj_hor, xerr=y_proj_st, fmt='-k.', zorder=1)
			self.proj_x.set_xlim(0,height*self.m)
			self.proj_y.set_ylim(0,width*self.m)
		
		# # # Fit Projections
		if self.FitX == 2:
			if self.selectFit_X == '1 Gauss':
				self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a00_err_x, self.a0_err_x,self.a1_err_x,self.a2_err_x,self.a3_err_x = gauss_fit_function(self.x_proj_hor,self.x_proj,np.mean(self.x_proj[0:10]),0,10,self.x_proj_hor[np.argmax(self.x_proj)],100*self.m/2)
				self.proj_x.plot(self.x_proj_hor, fit_func(self.x_proj_hor, self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x),color='r', zorder=2)
				self.fit_string_x.emit('Horizontal fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f'%(self.a00_x,self.a00_err_x,self.a0_x,self.a0_err_x,self.a1_x,self.a1_err_x,self.a2_x,self.a2_err_x,np.abs(self.a3_x),self.a3_err_x))
				if save == '1':
					print self.i
					string_to_write = '\t'.join(map(str, self.Values)) + '\t'+ str(self.a00_x)+"\t"+str(self.a00_err_x)+"\t"+str(self.a0_x)+"\t"+str(self.a0_err_x)+"\t"+ str(self.a1_x)+"\t"+ str(self.a1_err_x)+"\t"+ str(self.a2_x)+"\t"+ str(self.a2_err_x)+"\t"+ str(np.abs(self.a3_x))+"\t"+ str(self.a3_err_x)+"\t"+str(self.filelist[self.i])+"\n"
					if len(string_to_write) > 200:
						self.f.write(string_to_write)
					return self.a00_x
			if self.selectFit_X == 'Sk Gauss':
				self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a4_x,self.a00_err_x, self.a0_err_x,self.a1_err_x,self.a2_err_x,self.a3_err_x,self.a4_err_x = skew_gauss_fit_function(self.x_proj_hor,self.x_proj,np.mean(self.x_proj[0:10]),0,10,self.x_proj_hor[np.argmax(self.x_proj)],100*self.m/2, 0)
				self.proj_x.plot(self.x_proj_hor, skew_fit_func(self.x_proj_hor, self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a4_x),color='r', zorder=2)
				self.fit_string_x.emit('Horizontal fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Skew = %.2f -/+ %.2f'%(self.a00_x,self.a00_err_x,self.a0_x,self.a0_err_x,self.a1_x,self.a1_err_x,self.a2_x,self.a2_err_x,np.abs(self.a3_x),self.a3_err_x,self.a4_x,self.a4_err_x))
				if save == '1':
					print self.i
					string_to_write = '\t'.join(map(str, self.Values)) + '\t'+ str(self.a00_x)+"\t"+str(self.a00_err_x)+"\t"+str(self.a0_x)+"\t"+str(self.a0_err_x)+"\t"+ str(self.a1_x)+"\t"+ str(self.a1_err_x)+"\t"+ str(self.a2_x)+"\t"+ str(self.a2_err_x)+"\t"+ str(np.abs(self.a3_x))+"\t"+ str(self.a3_err_x)+"\t"+ str(np.abs(self.a4_x))+"\t"+ str(self.a4_err_x)+"\t"+str(self.filelist[self.i])+"\n"
					if len(string_to_write) > 200:
						self.f.write(string_to_write)
					return self.a00_x
			if self.selectFit_X == '2 Gauss':
				a = self.x_proj[(np.diff(np.sign(np.diff(self.x_proj))) < 0).nonzero()[0] + 1]
				b = a[np.argsort(self.x_proj[(np.diff(np.sign(np.diff(self.x_proj))) < 0).nonzero()[0] + 1])[-2:]] # "<0" - for max, 2 - for two peaks
				
				print self.x_proj_hor[np.where(self.x_proj==b[0])[0]]
				print self.x_proj_hor[np.where(self.x_proj==b[1])[0]]

				self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a11_x,self.a21_x,self.a31_x,self.a00_err_x, self.a0_err_x,self.a1_err_x,self.a2_err_x,self.a3_err_x,self.a11_err_x,self.a21_err_x,self.a31_err_x = two_gauss_fit_function(self.x_proj_hor,self.x_proj,np.mean(self.x_proj[0:10]),0,10,self.x_proj_hor[np.where(self.x_proj==b[0])[0]],100*self.m/2,10,self.x_proj_hor[np.where(self.x_proj==b[1])[0]],100*self.m/2)
				self.proj_x.plot(self.x_proj_hor, two_fit_func(self.x_proj_hor, self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a11_x,self.a21_x,self.a31_x),color='r', zorder=2)
				self.fit_string_x.emit('Horizontal fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n First peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Second peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Distance = %.2f -/+ %.2f'%(self.a00_x,self.a00_err_x,self.a0_x,self.a0_err_x,self.a1_x,self.a1_err_x,self.a2_x,self.a2_err_x,np.abs(self.a3_x),self.a3_err_x,self.a11_x,self.a11_err_x,self.a21_x,self.a21_err_x,np.abs(self.a31_x),self.a31_err_x, np.abs(self.a21_x - self.a2_x),np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x)))
				if save == '1':
					print self.i
					string_to_write = '\t'.join(map(str, self.Values)) + '\t'+ str(self.a00_x)+'\t'+str(self.a00_err_x)+'\t'+str(self.a0_x)+'\t'+str(self.a0_err_x)+'\t'+str(self.a1_x)+'\t'+str(self.a1_err_x)+'\t'+str(self.a2_x)+'\t'+str(self.a2_err_x)+'\t'+str(np.abs(self.a3_x))+'\t'+str(self.a3_err_x)+'\t'+str(self.a11_x)+'\t'+str(self.a11_err_x)+'\t'+str(self.a21_x)+'\t'+str(self.a21_err_x)+'\t'+str(np.abs(self.a31_x))+'\t'+str(self.a31_err_x)+'\t'+str( np.abs(self.a21_x - self.a2_x))+'\t'+str(np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x))+'\t'+str(self.filelist[self.i])+'\n'
					if len(string_to_write) > 380:
						self.f.write(string_to_write)
					return self.a00_x
			if self.selectFit_X == '2 Sk Gauss':
				a = self.x_proj[(np.diff(np.sign(np.diff(self.x_proj))) < 0).nonzero()[0] + 1]
				b = a[np.argsort(self.x_proj[(np.diff(np.sign(np.diff(self.x_proj))) < 0).nonzero()[0] + 1])[-2:]] # "<0" - for max, 2 - for two peaks
				
				print self.x_proj_hor[np.where(self.x_proj==b[0])[0]]
				print self.x_proj_hor[np.where(self.x_proj==b[1])[0]]

				self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a4_x,self.a11_x,self.a21_x,self.a31_x,self.a41_x,self.a00_err_x, self.a0_err_x,self.a1_err_x,self.a2_err_x,self.a3_err_x,self.a4_err_x,self.a11_err_x,self.a21_err_x,self.a31_err_x,self.a41_err_x = two_skew_gauss_fit_function(self.x_proj_hor,self.x_proj,np.mean(self.x_proj[0:10]),0,10,self.x_proj_hor[np.where(self.x_proj==b[0])[0]],100*self.m/2,0,10,self.x_proj_hor[np.where(self.x_proj==b[1])[0]],100*self.m/2,0)
				self.proj_x.plot(self.x_proj_hor, two_skew_fit_func(self.x_proj_hor, self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a4_x,self.a11_x,self.a21_x,self.a31_x,self.a41_x),color='r', zorder=2)
				self.fit_string_x.emit('Horizontal fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n First peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Skew = %.2f -/+ %.2f\n Second peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Skew = %.2f -/+ %.2f\n Distance = %.2f -/+ %.2f'%(self.a00_x,self.a00_err_x,self.a0_x,self.a0_err_x,self.a1_x,self.a1_err_x,self.a2_x,self.a2_err_x,np.abs(self.a3_x),self.a3_err_x,self.a4_x,self.a4_err_x,self.a11_x,self.a11_err_x,self.a21_x,self.a21_err_x,np.abs(self.a31_x),self.a31_err_x,self.a41_x,self.a41_err_x, np.abs(self.a21_x - self.a2_x),np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x)))
				if save == '1':
					print self.i
					string_to_write = '\t'.join(map(str, self.Values)) + '\t'+ str(self.a00_x)+'\t'+str(self.a00_err_x)+'\t'+str(self.a0_x)+'\t'+str(self.a0_err_x)+'\t'+str(self.a1_x)+'\t'+str(self.a1_err_x)+'\t'+str(self.a2_x)+'\t'+str(self.a2_err_x)+'\t'+str(np.abs(self.a3_x))+'\t'+str(self.a3_err_x)+'\t'+str(np.abs(self.a4_x))+'\t'+str(self.a4_err_x)+'\t'+str(self.a11_x)+'\t'+str(self.a11_err_x)+'\t'+str(self.a21_x)+'\t'+str(self.a21_err_x)+'\t'+str(np.abs(self.a31_x))+'\t'+str(self.a31_err_x)+'\t'+str(np.abs(self.a41_x))+'\t'+str(self.a41_err_x)+'\t'+str( np.abs(self.a21_x - self.a2_x))+'\t'+str(np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x))+'\t'+str(self.filelist[self.i])+'\n'
					if len(string_to_write) > 380:
						self.f.write(string_to_write)
					return self.a00_x
			if self.selectFit_X == '2 G_Fix':
				self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a11_x,self.a21_x,self.a31_x,self.a00_err_x, self.a0_err_x,self.a1_err_x,self.a2_err_x,self.a3_err_x,self.a11_err_x,self.a21_err_x,self.a31_err_x = two_gauss_fit_function_FixSigma(self.x_proj_hor,self.x_proj,np.mean(self.x_proj[0:10]),0,10,self.x_proj_hor[np.argmax(self.x_proj)],self.fix_sigma,10,self.x_proj_hor[np.argmax(self.x_proj)],self.fix_sigma)
				self.proj_x.plot(self.x_proj_hor, two_fit_func_fixSigma(self.x_proj_hor, self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a11_x,self.a21_x),color='r', zorder=2)
				self.a3_x = float(self.fix_sigma)
				self.a31_x = float(self.fix_sigma)
				self.fit_string_x.emit('Horizontal fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n First peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Second peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Distance = %.2f -/+ %.2f'%(self.a00_x,self.a00_err_x,self.a0_x,self.a0_err_x,self.a1_x,self.a1_err_x,self.a2_x,self.a2_err_x, self.a3_x,self.a3_err_x,self.a11_x,self.a11_err_x,self.a21_x,self.a21_err_x,self.a31_x,self.a31_err_x, np.abs(self.a21_x - self.a2_x),np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x)))
				if save == '1':
					print self.i
					self.f.write('\t'.join(map(str, self.Values)) + '\t'+ str(self.a00_x)+'\t'+str(self.a00_err_x)+'\t'+str(self.a0_x)+'\t'+str(self.a0_err_x)+'\t'+str(self.a1_x)+'\t'+str(self.a1_err_x)+'\t'+str(self.a2_x)+'\t'+str(self.a2_err_x)+'\t'+str(np.abs(self.a3_x))+'\t'+str(self.a3_err_x)+'\t'+str(self.a11_x)+'\t'+str(self.a11_err_x)+'\t'+str(self.a21_x)+'\t'+str(self.a21_err_x)+'\t'+str(np.abs(self.a31_x))+'\t'+str(self.a31_err_x)+'\t'+str( np.abs(self.a21_x - self.a2_x))+'\t'+str(np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x))+'\t'+str(self.filelist[self.i])+'\n')
					return self.a00_x
			if self.selectFit_X == '4 Gauss':
				
				peaks = self.x_proj_hor[argrelmax(ndimage.filters.gaussian_filter1d(self.x_proj, 15))[0]]
				
				self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a11_x,self.a21_x,self.a31_x,self.a12_x,self.a22_x,self.a32_x,self.a13_x,self.a23_x,self.a33_x,self.a00_err_x, self.a0_err_x,self.a1_err_x,self.a2_err_x,self.a3_err_x,self.a11_err_x,self.a21_err_x,self.a31_err_x,self.a12_err_x,self.a22_err_x,self.a32_err_x,self.a13_err_x,self.a23_err_x,self.a33_err_x = four_gauss_fit_function(self.x_proj_hor,self.x_proj,np.mean(self.x_proj[0:10]),0,10,peaks[0],100*self.m/2,10,peaks[1],100*self.m/2,10,peaks[2],100*self.m/2,10,peaks[3],100*self.m/2)
				self.proj_x.plot(self.x_proj_hor, four_fit_func(self.x_proj_hor, self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a11_x,self.a21_x,self.a31_x,self.a12_x,self.a22_x,self.a32_x,self.a13_x,self.a23_x,self.a33_x),color='r', zorder=2)
				self.fit_string_x.emit('Horizontal fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n First peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Second peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Third peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Forth peak:\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f\n Distance 1-2 = %.2f -/+ %.2f\n Distance 2-3 = %.2f -/+ %.2f\n Distance 3-4 = %.2f -/+ %.2f'%(self.a00_x,self.a00_err_x,self.a0_x,self.a0_err_x,self.a1_x,self.a1_err_x,self.a2_x,self.a2_err_x,np.abs(self.a3_x),self.a3_err_x,self.a11_x,self.a11_err_x,self.a21_x,self.a21_err_x,np.abs(self.a31_x),self.a31_err_x,self.a12_x,self.a12_err_x,self.a22_x,self.a22_err_x,np.abs(self.a32_x),self.a32_err_x,self.a13_x,self.a13_err_x,self.a23_x,self.a23_err_x,np.abs(self.a33_x),self.a33_err_x, np.abs(self.a21_x - self.a2_x),np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x), np.abs(self.a22_x - self.a21_x),np.sqrt(self.a21_err_x*self.a21_err_x+self.a22_err_x*self.a22_err_x), np.abs(self.a23_x - self.a22_x),np.sqrt(self.a22_err_x*self.a22_err_x+self.a23_err_x*self.a23_err_x)))
				if save == '1':
					print self.i
					self.f.write('\t'.join(map(str, self.Values)) + '\t'+ str(self.a00_x)+'\t'+str(self.a00_err_x)+'\t'+str(self.a0_x)+'\t'+str(self.a0_err_x)+'\t'+str(self.a1_x)+'\t'+str(self.a1_err_x)+'\t'+str(self.a2_x)+'\t'+str(self.a2_err_x)+'\t'+str(np.abs(self.a3_x))+'\t'+str(self.a3_err_x)+'\t'+str(self.a11_x)+'\t'+str(self.a11_err_x)+'\t'+str(self.a21_x)+'\t'+str(self.a21_err_x)+'\t'+str(np.abs(self.a31_x))+'\t'+str(self.a31_err_x)+'\t'+str(self.a12_x)+'\t'+str(self.a12_err_x)+'\t'+str(self.a22_x)+'\t'+str(self.a22_err_x)+'\t'+str(np.abs(self.a32_x))+'\t'+str(self.a32_err_x)+'\t'+str(self.a13_x)+'\t'+str(self.a13_err_x)+'\t'+str(self.a23_x)+'\t'+str(self.a23_err_x)+'\t'+str(np.abs(self.a33_x))+'\t'+str(self.a33_err_x)+'\t'+str( np.abs(self.a21_x - self.a2_x))+'\t'+str(np.sqrt(self.a2_err_x*self.a2_err_x+self.a21_err_x*self.a21_err_x))+'\t'+str(np.abs(self.a22_x - self.a21_x))+'\t'+str(np.sqrt(self.a21_err_x*self.a21_err_x+self.a22_err_x*self.a22_err_x))+'\t'+str(np.abs(self.a23_x - self.a22_x))+'\t'+str(np.sqrt(self.a22_err_x*self.a22_err_x+self.a23_err_x*self.a23_err_x))+'\t'+str(self.filelist[self.i])+'\n')
					return self.a00_x
		if self.FitY == 2:
			self.a00_y, self.a0_y,self.a1_y,self.a2_y,self.a3_y,self.a00_err_y, self.a0_err_y,self.a1_err_y,self.a2_err_y,self.a3_err_y = gauss_fit_function(self.y_proj_hor,self.y_proj,np.mean(self.y_proj[0:10]),0,10,self.y_proj_hor[np.argmax(self.y_proj)],100*self.m/2)
			self.proj_y.plot(fit_func(self.y_proj_hor, self.a00_y, self.a0_y,self.a1_y,self.a2_y,self.a3_y), self.y_proj_hor, color='r', zorder=2)
			self.fit_string_y.emit('Vertical fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f'%(self.a00_y,self.a00_err_y,self.a0_y,self.a0_err_y,self.a1_y,self.a1_err_y,self.a2_y,self.a2_err_y,np.abs(self.a3_y),self.a3_err_y))
		if self.FitXY == 2:
			self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x,self.a00_err_x, self.a0_err_x,self.a1_err_x,self.a2_err_x,self.a3_err_x = gauss_fit_function(self.x_proj_hor,self.x_proj,np.mean(self.x_proj[0:10]),0,10,self.x_proj_hor[np.argmax(self.x_proj)],100*self.m/2)
			self.proj_x.plot(self.x_proj_hor, fit_func(self.x_proj_hor, self.a00_x, self.a0_x,self.a1_x,self.a2_x,self.a3_x),color='r', zorder=2)
			self.a00_y, self.a0_y,self.a1_y,self.a2_y,self.a3_y,self.a00_err_y, self.a0_err_y,self.a1_err_y,self.a2_err_y,self.a3_err_y = gauss_fit_function(self.y_proj_hor,self.y_proj,np.mean(self.y_proj[0:10]),0,10,self.y_proj_hor[np.argmax(self.y_proj)],100*self.m/2)
			self.proj_y.plot(fit_func(self.y_proj_hor, self.a00_y, self.a0_y,self.a1_y,self.a2_y,self.a3_y), self.y_proj_hor, color='r', zorder=2)
			self.fit_string_x.emit('Horizontal fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f'%(self.a00_x,self.a00_err_x,self.a0_x,self.a0_err_x,self.a1_x,self.a1_err_x,self.a2_x,self.a2_err_x,np.abs(self.a3_x),self.a3_err_x))
			self.fit_string_y.emit('Vertical fit:\n ver. offset = %.2f -/+ %.2f\n Slope = %.2f -/+ %.2f\n Amplitude = %.2f -/+ %.2f\n hor. offset = %.2f -/+ %.2f\n Sigma = %.2f -/+ %.2f'%(self.a00_y,self.a00_err_y,self.a0_y,self.a0_err_y,self.a1_y,self.a1_err_y,self.a2_y,self.a2_err_y,np.abs(self.a3_y),self.a3_err_y))
			if save == '1':
					print self.i
					self.f.write(str(self.a00_x)+"\t"+str(self.a00_err_x)+"\t"+str(self.a0_x)+"\t"+str(self.a0_err_x)+"\t"+ str(self.a1_x)+"\t"+ str(self.a1_err_x)+"\t"+ str(self.a2_x)+"\t"+ str(self.a2_err_x)+"\t"+ str(np.abs(self.a3_x))+"\t"+ str(self.a3_err_x)+"\t"+str(self.a00_y)+"\t"+str(self.a00_err_y)+"\t"+str(self.a0_y)+"\t"+str(self.a0_err_y)+"\t"+ str(self.a1_y)+"\t"+ str(self.a1_err_y)+"\t"+ str(self.a2_y)+"\t"+ str(self.a2_err_y)+"\t"+ str(np.abs(self.a3_y))+"\t"+ str(self.a3_err_y)+"\t"+str(self.filelist[self.i])+"\n")
					return self.a00_x
		self.proj_y.invert_yaxis()
		# Changed on 15.12.21
		#self.draw()
		FigureCanvas.draw(self)
		#self.update()
		#self.repaint()
		
		# # Save Image or Background
		if len(self.FilenameToSave) != 0 and 'back' not in self.FilenameToSave:
			self.NameOfFile, self.NameOfFolder = save_image(self.startGetcounter, self.newimg, self.FilenameToSave, self.Screen, self.m, str(self.FilterSts), self.FilterSelect, self.FilterOrder, self.cursor_state, self.sld_h1_pos, self.sld_h2_pos, self.sld_v1_pos, self.sld_v2_pos)
			self.filename.emit(self.NameOfFile)
			self.foldername.emit(self.NameOfFolder)
			self.startGetcounter += 1
		elif len(self.FilenameToSave) != 0 and 'back' in self.FilenameToSave:
			self.NameOfFile, self.NameOfFolder = save_back(self.startGetcounter, self.newimg, self.FilenameToSave, self.Screen, self.m, self.FilterSts, self.FilterSelect, self.FilterOrder, self.cursor_state, self.sld_h1_pos, self.sld_h2_pos, self.sld_v1_pos, self.sld_v2_pos)
			self.backname.emit(self.NameOfFolder + '/' + self.NameOfFile)
			self.startGetcounter += 1
			
		if save == '1':
			self.i += 1
	
	def Updater(self):
		self.update_figure('0')
	
	def startGetcounter(self):
		self.startGetcounter = 0
		
	def getValue_Intensity_sld(self, value):
		self.scale = value
	def getValueSLD_h1(self, value):
		self.sld_h1_pos = value
	def getValueSLD_h2(self, value):
		self.sld_h2_pos = value
	def getValueSLD_v1(self, value):
		self.sld_v1_pos = value
	def getValueSLD_v2(self, value):
		self.sld_v2_pos = value
	def Cursors(self, state):
		self.cursor_state = state
		self.update_figure('0')
		
	def BackSbs(self, state):
		self.back_sbs = state
		self.update_figure('0')
		
	def BackFile(self, file):
		self.backimg, self.Header, self.Names, self.Values = imageOpener(file, self.Screen)
		self.update_figure('0')
	def ImgFile(self, file):
		self.dir, self.file = os.path.split(str(file))
		self.newimg, self.Header, self.Names, self.Values = imageOpener(file, self.Screen)
		self.update_figure('0')
		self.header_from_fit_file.emit(self.Header)
	def ImgFolder(self,folder,results):
		self.filelist = sorted(results)
		self.folder = folder
		self.dir = folder
		self.i = 0
		self.OneBy1_iter = 0
		self.newimg, self.Header, self.Names, self.Values = imageOpener(str(self.folder)+'/'+str(self.filelist[self.i]), self.Screen)
		self.update_figure('0')
		self.filename.emit(str(self.filelist[self.i]))
		self.file = str(self.filelist[self.i])
		self.header_from_fit_file.emit(self.Header)
		
	def FitX(self, state):
		self.FitX = state
		self.update_figure('0')
	def FitY(self, state):
		self.FitY = state
		self.update_figure('0')
	def FitXY(self, state):
		self.FitXY = state
		self.update_figure('0')
	def selectScreen(self, text):
		self.Screen = str(text)
		self.update_figure('0')
		
	def selectFilter(self, text):
		self.FilterSelect = str(text)
		self.update_figure('0')
	
	def Filter(self, text):
		self.FilterSts = text	
		self.update_figure('0')
		
	def FixSigma(self, value):
		self.fix_sigma = value
		
	def FilterOrder(self, text):
		self.FilterOrder = float(text)
		self.update_figure('0')
		
	def selectFitX(self, text):
		self.selectFit_X = text	
		self.update_figure('0')
	
	def AutoScale(self, state):
		self.autoscale = state
		
	def buttonFor(self):
		if len(self.filelist) != 0:
			if self.i < len(self.filelist):
				self.i +=1
			else:
				self.i = 0
			self.newimg, self.Header, self.Names, self.Values = imageOpener(str(self.folder)+'/'+str(self.filelist[self.i]), self.Screen)
			self.update_figure('0')
			self.filename.emit(str(self.filelist[self.i]))
			self.header_from_fit_file.emit(self.Header)
	def buttonRev(self):
		if len(self.filelist) != 0:
			if self.i < len(self.filelist):
				self.i -=1
			else:
				self.i = 0
			self.newimg, self.Header, self.Names, self.Values = imageOpener(str(self.folder)+'/'+str(self.filelist[self.i]), self.Screen)
			self.update_figure('0')
			self.filename.emit(str(self.filelist[self.i]))
			self.header_from_fit_file.emit(self.Header)
	def FilenameToSave(self, text):
		self.FilenameToSave = str(text)
		
	def SetDefaults(self):
		self.FilterOrder = 3
		self.FilenameToSave = ''

	def ProcAll(self, **kwargs):
		if len(self.filelist) != 0:
			for self.i in range(0, len(self.filelist)):
				if self.i == 0:
					filename = "/Users/konstantin/Documents/analysis/"+time.strftime("%y_%m_%d")+"/"+time.strftime("%y_%m_%d")+time.strftime("_%H_%M_%S")+"_"+str(self.filelist[0])+'Proc_All'+".txt"
					dir, file = os.path.split(filename)
					create_folder(dir)
					self.f = open('%s' % filename, "w")
					self.f.write("ver.02" + "\n" + "\n")
					self.f.write(dir + "\n" + "\n")
					self.f.write("ProcAll, "+ filename + "\n" + "\n")
					self.f.write("Trigger valiable:"+"\t"+' '+"\t"+"Vertical centroid position, microns"+"\n"
					     "Scanning variable:"+"\t"+' '+"\t"+"Horizontal centroid position, microns"+"\n" + "\n")
					self.newimg, self.Header, self.Names, self.Values = imageOpener(str(self.folder)+'/'+str(self.filelist[1]))
					self.f.write(', '.join(map(str, self.Names)) + ', ' + 'a00+a0*x+a1*np.exp(-((x-a2)**2)/(2*a3**2))'+"\t"+'or Sum of Gaussians'+"\n") ######## COLUMN NAMES ##########
					self.f.write("***" + "\n")
				
				self.newimg, self.Header, self.Names, self.Values = imageOpener(str(self.folder)+'/'+str(self.filelist[self.i]), self.Screen)
				self.filename.emit(str(self.filelist[self.i]))
				self.a00_x = self.update_figure('1')
			self.f.close()
		else: 
			QMessageBox.about(self, "Error !", " ---=== <<< Set Folder >>> === ---")

	def OneBy1(self, **kwargs):
			if len(self.filelist) != 0:
				if self.OneBy1_iter == 0:
					filename = "/Users/konstantin/Documents/analysis/"+time.strftime("%y_%m_%d")+"/"+time.strftime("%y_%m_%d")+time.strftime("_%H_%M_%S")+"_"+self.FilenameToSave+'Proc_All'+".txt"
					dir, file = os.path.split(filename)
					create_folder(dir)
					self.f = open('%s' % filename, "w")
					self.f.write("ver.02" + "\n" + "\n")
					self.f.write(dir + "\n" + "\n")
					self.f.write("ProcAll, "+ filename + "\n" + "\n")
					self.f.write("Trigger valiable:"+"\t"+' '+"\t"+"Vertical centroid position, microns"+"\n"
					     "Scanning variable:"+"\t"+' '+"\t"+"Horizontal centroid position, microns"+"\n" + "\n")
					self.newimg, self.Header, self.Names, self.Values = imageOpener(str(self.folder)+'/'+str(self.filelist[1]), self.Screen)
					self.f.write(', '.join(map(str, self.Names)) + ', ' + 'a00+a0*x+a1*np.exp(-((x-a2)**2)/(2*a3**2))'+"\t"+'or Sum of Gaussians'+"\n") ######## COLUMN NAMES ##########
					self.f.write("***" + "\n")
					self.OneBy1_iter = 1
			
			self.newimg, self.Header, self.Names, self.Values = imageOpener(str(self.folder)+'/'+str(self.filelist[self.i]), self.Screen)
			self.filename.emit(str(self.filelist[self.i]))
			self.a00_x = self.update_figure('1')
			
	def buttonFileClose(self):
		self.f.close()
		self.OneBy1_iter = 0
		
	def save(self):
		p = QPixmap.grabWindow(win.winId())
		#p = QScreen.grabWindow(win.winId())
		filename = "/Users/konstantin/Documents/analysis/"+time.strftime("%y_%m_%d")+"/"+time.strftime("%y_%m_%d")+time.strftime("_%H_%M_%S")+'_prscreen'
		dir, file = os.path.split(filename)
		create_folder(dir)
		p.save(dir+'/'+file, 'png')
		#self.fig.savefig(self.dir+'/'+self.file.split('.')[0] +'.png', format='png')#,dpi=100, figsize=(8, 6))
		QMessageBox.about(self, "Image saved as: ", dir+'/'+file+'.png')
		
def main(args):
	global win
	app=QApplication(args)
	win=MainWindow()
	win.show()
	app.exec_()

if __name__=="__main__":
	main(sys.argv)
