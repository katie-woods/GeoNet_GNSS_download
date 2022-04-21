#!/usr/bin/python3

import glob
import pandas as pd
import os

output_file='tdefnode_time_series/CS_LG_EK_coseismic_corrected_time_series.ts1'
#output_file='tdefnode_time_series/time_series.ts1'
os.remove(output_file)

# list csv files
input_files=glob.glob("CS_LG_EK_coseis_corrected_time_series/*.csv")
#input_files=glob.glob("time_series/*.csv")
input_files.sort()

# get GNSS interseismic/SSE velocities
veloc_dec_places = {'longitude': 4,
					'latitude': 4,
					'e': 2,
					'e_sig': 2,
					'n': 2,
					'n_sig': 2,
					'u': 2,
					'u_sig': 2 }
col_names=["longitude", "latitude", "e", "n", "u", "e_sig", "n_sig", "u_sig", "site"]
gnss_velocities=pd.read_csv('stations_gps.txt', delimiter=' ', header=None, names = col_names)
gnss_velocities=gnss_velocities.round(veloc_dec_places)
print(gnss_velocities)

# loop through sites and add interseismic velocity header
for disp_filename in input_files:
	site=disp_filename[38:42]
	#site=disp_filename[12:16]
	print(site)
	
	header_line = gnss_velocities[gnss_velocities['site'].str.contains(site)]
	print(header_line)

	header_line=header_line.to_csv(header=None, index=False, sep=' ')
	
	disp_data=pd.read_csv(disp_filename, delimiter=',')
	time_series_dec_places = {'decimal_year': 6,
							'e_mm': 2,
							'e_mm_sig': 2,
							'n_mm': 2,
							'n_mm_sig': 2,
							'u_mm': 2,
							'u_mm_sig': 2 }
	disp_data=disp_data.round(time_series_dec_places)
	disp_data=disp_data[['decimal_year', 'e_mm', 'e_mm_sig', 'n_mm', 'n_mm_sig', 'u_mm', 'u_mm_sig']]
	disp_data=disp_data.to_csv(header=None, index=False, sep=' ')
	
	with open(output_file, 'a') as file:
		file.writelines(' ' + header_line)
		for line in disp_data:
			file.writelines(line)
		file.writelines("9999.0\n")

