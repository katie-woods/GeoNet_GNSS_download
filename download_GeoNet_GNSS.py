#!/usr/bin/python3

''' Script to download the GeoNet GNSS east, north, and up time series, 
convert to decimal years (for TDEFNODE input), and correct for the 
21 July 2013 Cook Strait, 16 August 2013 Lake Grassmere, and 20 January
2014 Eketahuna earthquakes.
'''

import pandas as pd
import requests
from io import BytesIO
import datetime

# functions
def load_coseismic_displacements(disp_filename, origintime):
	col_names=["longitude", "latitude", "e_mm", "n_mm", "e_sig", "n_sig", "site", "u_mm", "u_sig"]
	disp_data=pd.read_csv(disp_filename, delimiter=' ', header=None, names = col_names)
	disp_sites = set(disp_data['site'])
	eq_time = float(datetime_to_decimalyear([origintime]))
	return disp_data, disp_sites, eq_time
	
def datetime_to_decimalyear(datetime_var):
	data = pd.DataFrame(columns = ["date-time"])
	data["date-time"] = pd.to_datetime(datetime_var)
	data["leap_year"] = data["date-time"].dt.is_leap_year.astype(int)
	data["year"] = pd.DatetimeIndex(data['date-time']).year.astype(float)
	data["day_of_year"] = pd.DatetimeIndex(data['date-time']).dayofyear.astype(float)
	data["hour"] = pd.DatetimeIndex(data['date-time']).hour.astype(float)
	data["minute"] = pd.DatetimeIndex(data['date-time']).minute.astype(float)
	data['decimal_year'] = data["year"] + (data["day_of_year"] + (data["hour"]/24) + (data["minute"]/(24*60)) ) / (365 + data["leap_year"])
	return data['decimal_year']

def get_GeoNet_GNSS_data(site, component):
	params = {'siteID': site,
			'typeID': component}
	base_url = 'http://fits.geonet.org.nz/observation'
	r = requests.get(base_url, params=params)
	data = pd.read_csv(BytesIO(r.content))
	return data

def correct_offset(site, sitelist, coseis_vars, eq_time, data, component):
	if site in sitelist:
		which_disp = coseis_vars['site'].str.contains(site)
		disp_index=which_disp.index[which_disp == True].tolist()
		time_index = data[data['decimal_year'].gt(eq_time)].index
		displacement=coseis_vars.loc[disp_index, [component]].values
		#print(site, eq_time, displacement)
		data.loc[time_index, [component]] = data.loc[time_index, [component]] - displacement
	return data

# components to download and time
comp2download=['e', 'n', 'u']

# set GeoNet site names to be downloaded
GeoNet_sites=pd.read_csv('sites', header=None, names =["site"])
sites=list(GeoNet_sites["site"])

# load coseismic displacements
[CS, CS_sites, CS_time] = load_coseismic_displacements('hamling_2014_CS_horiz_disp.txt', '2013-07-21 05:09:00+00:00')
[LG, LG_sites, LG_time] = load_coseismic_displacements('hamling_2014_LG_merged_disp.txt', '2013-08-16 02:31:00+00:00')
[EK, EK_sites, EK_time] = load_coseismic_displacements('eketahuna_coseismic_disp_ds2.txt', '2014-01-20 02:52:00+00:00')

# loop through sites
for site in sites:

	# initialise output dataframe
	output_data = pd.DataFrame(columns = ["date-time","decimal_year", "e_mm", "e_mm_sig", "n_mm", "n_mm_sig", "u_mm", "u_mm_sig",])
	
	# loop through E N U components
	for comp in comp2download:
	
		# set component label
		comp_label=str(comp+'_mm')
	
		# download GNSS data
		data=get_GeoNet_GNSS_data(site, comp)
		data.columns = ['date-time',comp_label,'sig_mm']
	
		# convert downloaded data to decimal year
		data['decimal_year'] = datetime_to_decimalyear(data['date-time'])
		
		# correct for coseismic displacements
		data=correct_offset(site, CS_sites, CS, CS_time, data, comp_label)
		data=correct_offset(site, LG_sites, LG, LG_time, data, comp_label)
		data=correct_offset(site, EK_sites, EK, EK_time, data, comp_label)
		
		# append component to output dataframe
		output_data['date-time'] = data['date-time']
		output_data['decimal_year'] = data['decimal_year']
		output_data[comp_label] = data[comp_label]
		output_data[str(comp_label+'_sig')] = data['sig_mm']
		
	# save GNSS site to csv
	out_name=str('coseis_corrected/'+site+'.csv')
	output_data.to_csv(out_name, index = False)
