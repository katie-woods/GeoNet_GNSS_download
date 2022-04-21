#!/usr/bin/python3

import glob
import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

def autoscale_y(ax,margin=0.1):
	"""This function rescales the y-axis based on the data that is visible given the current xlim of the axis.
	ax -- a matplotlib axes object
	margin -- the fraction of the total height of the y-data to pad the upper and lower ylims"""
	import numpy as np
	
	def get_bottom_top(line):
		xd = line.get_xdata()
		yd = line.get_ydata()
		lo,hi = ax.get_xlim()
		y_displayed = yd[((xd>lo) & (xd<hi))]
		h = np.max(y_displayed) - np.min(y_displayed)
		bot = np.min(y_displayed)-margin*h
		top = np.max(y_displayed)+margin*h
		return bot,top
	
	lines = ax.get_lines()
	bot,top = np.inf, -np.inf
	
	for line in lines:
		new_bot, new_top = get_bottom_top(line)
		if new_bot < bot: bot = new_bot
		if new_top > top: top = new_top
		
	ax.set_ylim(bot,top)

input_files=glob.glob("coseis_corrected/*.csv")

for disp_filename in input_files:
	site=disp_filename[17:21]
	print(site)
	disp_data=pd.read_csv(disp_filename, delimiter=',')

	

	components=['e_mm', 'n_mm', 'u_mm']
	ax= disp_data.plot(x = 'decimal_year', y = components, kind="line", 
						subplots = True, xlim=[2013.5, 2014.2], zorder=1,
						title = site, legend=False)
	autoscale_y(ax[0])
	autoscale_y(ax[1])
	autoscale_y(ax[2])

	for time in [2013.554014, 2013.624945, 2014.055123]:
		ax[0].axvline(time, color='k', linestyle='--', zorder = 2)
		ax[1].axvline(time, color='k', linestyle='--', zorder = 2)
		ax[2].axvline(time, color='k', linestyle='--', zorder = 2)
	
	plt.savefig('figures/'+site+'.png')
