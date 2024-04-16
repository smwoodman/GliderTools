# import os
# import xarray as xr
import glidertools as gt

filenames = 'C:/SMW/Gliders_Moorings/Gliders/GliderTools/tests/data/p5420*.nc'
names = [
    'ctd_depth',
    'ctd_time',
    'ctd_pressure',
    'salinity',
    'temperature',
    'eng_wlbb2flvmt_Chlsig',
    'eng_wlbb2flvmt_wl470sig',
    'eng_wlbb2flvmt_wl700sig',
    'aanderaa4330_dissolved_oxygen',
    'eng_qsp_PARuV',
]
ds_dict = gt.load.seaglider_basestation_netCDFs(
    filenames, names, return_merged=True, keep_global_attrs=False)

merged = ds_dict['merged']
if 'time' in merged:
    merged = merged.drop(["time", "time_dt64"])
    
dat = merged.rename({
    'salinity': 'salt_raw',
    'temperature': 'temp_raw',
    'ctd_pressure': 'pressure',
    'ctd_depth': 'depth',
    'ctd_time_dt64': 'time',
    'ctd_time': 'time_raw',
    'eng_wlbb2flvmt_wl700sig': 'bb700_raw',
    'eng_wlbb2flvmt_wl470sig': 'bb470_raw',
    'eng_wlbb2flvmt_Chlsig': 'flr_raw',
    'eng_qsp_PARuV': 'par_raw',
    'aanderaa4330_dissolved_oxygen': 'oxy_raw',
})

# variable assignment for conveniant access
depth = dat.depth
dives = dat.dives
lats = dat.latitude
lons = dat.longitude
time = dat.time
pres = dat.pressure
temp = dat.temp_raw
salt = dat.salt_raw
par = dat.par_raw
bb700 = dat.bb700_raw
bb470 = dat.bb470_raw
fluor = dat.flr_raw

bbp_baseline, bbp_spikes = gt.processing.calc_backscatter(
    bb700, temp, salt, dives, depth, 700, 49, 3.217e-5, 
    spike_window=11, spike_method='minmax', iqr=2., profiles_ref_depth=300,
    deep_multiplier=1, deep_method='median', verbose=True)
dat['bbp700'] = bbp_baseline

flr_qnch, flr, qnch_layer, [fig1, fig2] = gt.processing.calc_fluorescence(
    fluor, dat.bbp700, dives, depth, time, lats, lons, 53, 0.0121,
    profiles_ref_depth=300, deep_method='mean', deep_multiplier=1,
    spike_window=11, spike_method='median', return_figure=True, 
    night_day_group=False, sunrise_sunset_offset=2, verbose=True)

# dat['flr_qc'] = flr