#!/usr/bin/env python2.7

import numpy as np
from scipy.optimize import curve_fit

def fit_func(x,a00,a0,a1,a2,a3):
     return a00+a0*x+a1*np.exp(-((x-a2)**2)/(2*a3**2))

def skew_fit_func(x,a00,a0,a1,a2,a3,a4):
     return a00+a0*x+a1*np.exp(-((x-a2)**2)/(2*a3**2*(1+a4*np.sign(x-a2))**2))

def two_fit_func(x,a00,a0,a1,a2,a3,a11,a21,a31):
     return a00+a0*x+a1*np.exp(-((x-a2)**2)/(2*a3**2))+a11*np.exp(-((x-a21)**2)/(2*a31**2))
     
def two_skew_fit_func(x,a00,a0,a1,a2,a3,a4,a11,a21,a31,a41):
     return a00+a0*x+a1*np.exp(-((x-a2)**2)/(2*a3**2*(1+a4*np.sign(x-a2))**2))+a11*np.exp(-((x-a21)**2)/(2*a31**2*(1+a41*np.sign(x-a21))**2))
     
def two_fit_func_fixSigma(x,a00,a0,a1,a2,a11,a21):
     return a00+a0*x+a1*np.exp(-((x-a2)**2)/(2*fix_sigma**2))+a11*np.exp(-((x-a21)**2)/(2*fix_sigma**2))

def four_fit_func(x,a00,a0,a10,a20,a30,a11,a21,a31,a12,a22,a32,a13,a23,a33):
     return a00+a0*x+a10*np.exp(-((x-a20)**2)/(2*a30**2))+a11*np.exp(-((x-a21)**2)/(2*a31**2))+a12*np.exp(-((x-a22)**2)/(2*a32**2))+a13*np.exp(-((x-a23)**2)/(2*a33**2))

def gauss_fit_function(X, Y, a00_init,a0_init,a1_init,a2_init,a3_init):
	try:
		fit_params,fit_covariances = curve_fit(fit_func,X,Y,[a00_init,a0_init,a1_init,a2_init,a3_init], maxfev=500)
	except RuntimeError:
		fit_params,fit_covariances = [np.mean(Y),0,0,0,1],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
		
	#Fit parameters
	[a00, a0,a1,a2,a3]=fit_params
	
	# Errors of the fit params are square roots of the diagonal elements of the covariance matrix. 
	[a00_err, a0_err,a1_err,a2_err,a3_err] = [(fit_covariances[0][0])**0.5,(fit_covariances[1][1])**0.5,(fit_covariances[2][2])**0.5,(fit_covariances[3][3])**0.5,(fit_covariances[4][4])**0.5]
	
	chi_squared = np.sum(((fit_func(X, a00, a0,a1,a2,a3)-Y)/1)**2)
	reduced_chi_squared = (chi_squared)/(len(X)-len(fit_params))     
	#print chi_squared
	#print reduced_chi_squared 
	
	return a00, a0,a1,a2,a3,a00_err, a0_err,a1_err,a2_err,a3_err

def skew_gauss_fit_function(X, Y, a00_init,a0_init,a1_init,a2_init,a3_init,a4_init):
	try:
		fit_params,fit_covariances = curve_fit(skew_fit_func,X,Y,[a00_init,a0_init,a1_init,a2_init,a3_init,a4_init], maxfev=500)
	except RuntimeError:
		fit_params,fit_covariances = [np.mean(Y),0,0,0,1,0],[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
		
	#Fit parameters
	[a00, a0,a1,a2,a3,a4]=fit_params
	
	# Errors of the fit params are square roots of the diagonal elements of the covariance matrix. 
	[a00_err, a0_err,a1_err,a2_err,a3_err,a4_err] = [(fit_covariances[0][0])**0.5,(fit_covariances[1][1])**0.5,(fit_covariances[2][2])**0.5,(fit_covariances[3][3])**0.5,(fit_covariances[4][4])**0.5,(fit_covariances[5][5])**0.5]
	
	chi_squared = np.sum(((skew_fit_func(X, a00, a0,a1,a2,a3,a4)-Y)/1)**2)
	reduced_chi_squared = (chi_squared)/(len(X)-len(fit_params))     
	#print chi_squared
	#print reduced_chi_squared 
	
	return a00, a0,a1,a2,a3,a4,a00_err, a0_err,a1_err,a2_err,a3_err,a4_err
	
def two_gauss_fit_function(X, Y, a00_init,a0_init,a1_init,a2_init,a3_init,a11_init,a21_init,a31_init):
	try:
		fit_params,fit_covariances = curve_fit(two_fit_func,X,Y,[a00_init,a0_init,a1_init,a2_init,a3_init,a11_init,a21_init,a31_init], maxfev=1500)
	except RuntimeError:
		fit_params,fit_covariances = [np.mean(Y),0,0,0,1,0,0,1],[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
		
	#Fit parameters
	[a00, a0,a1,a2,a3,a11,a21,a31]=fit_params
	
	# Errors of the fit params are square roots of the diagonal elements of the covariance matrix. 
	[a00_err, a0_err,a1_err,a2_err,a3_err,a11_err,a21_err,a31_err] = [(fit_covariances[0][0])**0.5,(fit_covariances[1][1])**0.5,(fit_covariances[2][2])**0.5,(fit_covariances[3][3])**0.5,(fit_covariances[4][4])**0.5,(fit_covariances[5][5])**0.5,(fit_covariances[6][6])**0.5,(fit_covariances[7][7])**0.5]
	
	chi_squared = np.sum(((two_fit_func(X, a00, a0,a1,a2,a3,a11,a21,a31)-Y)/1)**2)
	reduced_chi_squared = (chi_squared)/(len(X)-len(fit_params))     
	#print chi_squared
	#print reduced_chi_squared 
	
	return a00, a0,a1,a2,a3,a11,a21,a31,a00_err, a0_err,a1_err,a2_err,a3_err,a11_err,a21_err,a31_err

def two_skew_gauss_fit_function(X, Y, a00_init,a0_init,a1_init,a2_init,a3_init,a4_init,a11_init,a21_init,a31_init,a41_init):
	try:
		fit_params,fit_covariances = curve_fit(two_skew_fit_func,X,Y,[a00_init,a0_init,a1_init,a2_init,a3_init,a4_init,a11_init,a21_init,a31_init,a41_init], maxfev=1500)
	except RuntimeError:
		fit_params,fit_covariances = [np.mean(Y),0,0,0,1,0,0,0,1,0],[[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]
		
	#Fit parameters
	[a00, a0,a1,a2,a3,a4,a11,a21,a31,a41]=fit_params
	
	# Errors of the fit params are square roots of the diagonal elements of the covariance matrix. 
	[a00_err, a0_err,a1_err,a2_err,a3_err,a4_err,a11_err,a21_err,a31_err,a41_err] = [(fit_covariances[0][0])**0.5,(fit_covariances[1][1])**0.5,(fit_covariances[2][2])**0.5,(fit_covariances[3][3])**0.5,(fit_covariances[4][4])**0.5,(fit_covariances[5][5])**0.5,(fit_covariances[6][6])**0.5,(fit_covariances[7][7])**0.5,(fit_covariances[8][8])**0.5,(fit_covariances[9][9])**0.5]
	
	chi_squared = np.sum(((two_skew_fit_func(X, a00, a0,a1,a2,a3,a4,a11,a21,a31,a41)-Y)/1)**2)
	reduced_chi_squared = (chi_squared)/(len(X)-len(fit_params))     
	#print chi_squared
	#print reduced_chi_squared 
	
	return a00, a0,a1,a2,a3,a4,a11,a21,a31,a41,a00_err, a0_err,a1_err,a2_err,a3_err,a4_err,a11_err,a21_err,a31_err,a41_err

def two_gauss_fit_function_FixSigma(X, Y, a00_init,a0_init,a1_init,a2_init,fix_sigma_g,a11_init,a21_init,a31_init):
	global fix_sigma
	fix_sigma = int(fix_sigma_g)
	
	try:
		fit_params,fit_covariances = curve_fit(two_fit_func_fixSigma,X,Y,[a00_init,a0_init,a1_init,a2_init,a11_init,a21_init], maxfev=500)
	except RuntimeError:
		fit_params,fit_covariances = [np.mean(Y),0,0,0,0,0],[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
		
	#Fit parameters
	[a00, a0,a1,a2,a11,a21]=fit_params
	
	# Errors of the fit params are square roots of the diagonal elements of the covariance matrix. 
	[a00_err, a0_err,a1_err,a2_err,a11_err,a21_err] = [(fit_covariances[0][0])**0.5,(fit_covariances[1][1])**0.5,(fit_covariances[2][2])**0.5,(fit_covariances[3][3])**0.5,(fit_covariances[4][4])**0.5,(fit_covariances[5][5])**0.5]

	return a00, a0,a1,a2,fix_sigma,a11,a21,fix_sigma,a00_err, a0_err,a1_err,a2_err, 0,a11_err,a21_err, 0

def four_gauss_fit_function(X, Y, a00_init,a0_init,a1_init,a2_init,a3_init,a11_init,a21_init,a31_init,a12_init,a22_init,a32_init,a13_init,a23_init,a33_init):
	try:
		fit_params,fit_covariances = curve_fit(four_fit_func,X,Y,[a00_init,a0_init,a1_init,a2_init,a3_init,a11_init,a21_init,a31_init,a12_init,a22_init,a32_init,a13_init,a23_init,a33_init], maxfev=1500)
	except RuntimeError:
		fit_params,fit_covariances = [np.mean(Y),0,0,0,1,0,0,1,0,0,1,0,0,1],[[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
		
	#Fit parameters
	[a00, a0,a1,a2,a3,a11,a21,a31,a12,a22,a32,a13,a23,a33]=fit_params
	
	# Errors of the fit params are square roots of the diagonal elements of the covariance matrix. 
	[a00_err, a0_err,a1_err,a2_err,a3_err,a11_err,a21_err,a31_err,a12_err,a22_err,a32_err,a13_err,a23_err,a33_err] = [(fit_covariances[0][0])**0.5,(fit_covariances[1][1])**0.5,(fit_covariances[2][2])**0.5,(fit_covariances[3][3])**0.5,(fit_covariances[4][4])**0.5,(fit_covariances[5][5])**0.5,(fit_covariances[6][6])**0.5,(fit_covariances[7][7])**0.5,(fit_covariances[8][8])**0.5,(fit_covariances[9][9])**0.5,(fit_covariances[10][10])**0.5,(fit_covariances[11][11])**0.5,(fit_covariances[12][12])**0.5,(fit_covariances[13][13])**0.5]

	return a00, a0,a1,a2,a3,a11,a21,a31,a12,a22,a32,a13,a23,a33,a00_err, a0_err,a1_err,a2_err,a3_err,a11_err,a21_err,a31_err,a12_err,a22_err,a32_err,a13_err,a23_err,a33_err
