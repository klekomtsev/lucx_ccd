#!/usr/bin/env python2.7

import numpy as np
import scipy
from scipy import ndimage
from skimage.restoration import denoise_tv_chambolle, denoise_bilateral

def BF_proc(newimg, backimg, FilterSts, FilterOrder, FilterSelect, back_sbs):
	
	if back_sbs == 2 and FilterSts == 2:
		if FilterSelect == 'Median':
			ImageFinal = ndimage.median_filter(np.subtract(newimg, backimg), FilterOrder)
		elif FilterSelect == 'Gaussian':
			ImageFinal = ndimage.gaussian_filter(np.subtract(newimg, backimg), FilterOrder)
		elif FilterSelect == 'Uniform':
			ImageFinal = ndimage.uniform_filter(np.subtract(newimg, backimg), FilterOrder)
		elif FilterSelect == 'Denoise TV':
			ImageFinal = denoise_tv_chambolle(np.subtract(newimg, backimg), weight=FilterOrder, multichannel=True)
		elif FilterSelect == 'Bilateral':
			ImageFinal = denoise_bilateral(np.subtract(newimg, backimg), sigma_range=FilterOrder, sigma_spatial=15)	
	elif back_sbs == 2 and FilterSts == 0:
		ImageFinal = np.subtract(newimg, backimg)
	elif back_sbs == 0 and FilterSts == 2:
		if FilterSelect == 'Median':
			ImageFinal = ndimage.median_filter(newimg, FilterOrder)
		elif FilterSelect == 'Gaussian':
			ImageFinal = ndimage.gaussian_filter(newimg, FilterOrder)
		elif FilterSelect == 'Uniform':
			ImageFinal = ndimage.uniform_filter(newimg, FilterOrder)
		elif FilterSelect == 'Denoise TV':
			ImageFinal = denoise_tv_chambolle(newimg, weight=FilterOrder, multichannel=True)
		elif FilterSelect == 'Bilateral':
			ImageFinal = denoise_bilateral(newimg, sigma_range=FilterOrder, sigma_spatial=15)	
	elif back_sbs == 0 and FilterSts == 0:
		ImageFinal = newimg
	
	return ImageFinal
	
