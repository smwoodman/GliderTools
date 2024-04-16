import os
import xarray as xr
import glidertools as gt

# filenames = 'C:/SMW/Gliders_Moorings/Gliders/GliderTools/tests/data/p5420*.nc'

# names = [
#     'ctd_depth',
#     'ctd_time',
#     'ctd_pressure',
#     'salinity',
#     'temperature',
#     'eng_wlbb2flvmt_Chlsig',
#     'eng_wlbb2flvmt_wl470sig',
#     'eng_wlbb2flvmt_wl700sig',
#     'aanderaa4330_dissolved_oxygen',
#     'eng_qsp_PARuV',
# ]

# ds_dict = gt.load.seaglider_basestation_netCDFs(
#     filenames, names, return_merged=True, keep_global_attrs=False)

deployment = 'amlr03-20230620'
project = 'SANDIEGO'
yr = '2023'
mode = 'delayed'
data_path = os.path.join("C:/SMW/Gliders_Moorings/Gliders/Glider-Data", 
                         project, yr, deployment, 'glider', 'data')
nc_ngdac_path = os.path.join(data_path, 'out', 'nc', 'ngdac', mode)
ds_list = []

for i in os.listdir(nc_ngdac_path):
    ds_tmp = xr.open_dataset(os.path.join(nc_ngdac_path, i))
    ds_list.append(ds_tmp)
ds = xr.concat(ds_list, dim="time")

df = ds[['profile_id', 'profile_direction']].to_pandas()
df['profile_id_dup'] = df.profile_id.duplicated(keep='first')
df['profile_id_cumsum'] = df.profile_id_dup.eq(False).cumsum()
df['dive'] = df.profile_id_cumsum / 2 + 0.5

ds["dives"] = (["time"], df.dive)
# ds

###
temp_qc = gt.calc_physics(ds.temperature, ds.dives, ds.idepth, 
                          iqr=1.5, depth_threshold=0,
                          spike_window=5, spike_method='median',
                          savitzky_golay_window=11, savitzky_golay_order=2)

salt_qc = gt.calc_physics(ds.salinity, ds.dives, ds.idepth, 
                          mask_frac=0.2, iqr=2.5, 
                          spike_window=5, spike_method='median', 
                          savitzky_golay_window=11, savitzky_golay_order=2)

ds['temp_qc'] = temp_qc
ds['salt_qc'] = salt_qc

###
dens0 = gt.physics.potential_density(
    ds.salt_qc, ds.temp_qc, ds.pressure, ds.lat, ds.lon)
ds['dens0'] = dens0

mld = gt.physics.mixed_layer_depth(ds, "dens0")

print(mld)
