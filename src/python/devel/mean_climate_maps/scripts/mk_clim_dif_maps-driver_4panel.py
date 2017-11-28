import vcs
import cdms2, cdutil, genutil
import MV2
import sys,os
import json
import string
import pcmdi_metrics
import time
import EzTemplate
import collections

from pcmdi_metrics.pcmdi.pmp_parser import PMPParser

P = PMPParser()

P.add_argument("-e", "--experiment",
                   type=str,
                   dest="experiment",
                   default="historical",
                   help="historical / amip / picontrol")
P.add_argument("-o", "--option",
                   type=int,
                   dest="option",
                   default=1,
                   help="1: mean clim, 2: remove zonal mean, 3: remove annual mean")
P.add_argument("--outdir",
                   type=str,
                   dest="outdir",
                   default="./test",
                   help="output directory path. The directory will be created automatically if not exist")
P.add_argument("-d", "--debug",
                   type=bool,
                   dest="debug",
                   default=False,
                   help="debug")

parameter = P.get_parameter()

#----------------------------------------------------------------------------
def remove_zonal_mean(d):
  d_zm = cdutil.averager(d,axis='x')
  d,d_zm = genutil.grower(d,d_zm) # Matching dimension for subtraction
  d = MV2.subtract(d, d_zm)  
  return d

def remove_annual_mean(ds, d):
  d_am = cdutil.YEAR.climatology(d)
  ds = MV2.subtract(ds, d_am)
  return ds
#----------------------------------------------------------------------------
debug = parameter.debug

OgridAsCommon = True
#OgridAsCommon = False # In case if OBS has higher resolution than models AND all models already have been processed to have same grid

#----------------------------------------------------------------------------
option = parameter.option

if option == 1:
  RemoveZonalMean = False
  RemoveAnnualMean = False
  odir = 'clim'
elif option == 2:
  RemoveZonalMean = True
  RemoveAnnualMean = False
  odir = 'climmzm'
elif option == 3:
  RemoveZonalMean = False
  RemoveAnnualMean = True
  odir = 'climmtm'

#----------------------------------------------------------------------------

era = 'cmip5'
exp = parameter.experiment

m = 'crunchy'

if m == 'oceanonly':
 basedir = '/work/gleckler1/'

if m == 'crunchy':
 basedir = '/export_backup/gleckler1/'

plots_outdir = parameter.outdir 

# Load the obs dictionary
#fjson = open(
#        os.path.join(
#            sys.prefix,
#            "share",
#            "pmp",
#            "obs_info_dictionary.json"))
fjson = open('../../../../../doc/obs_info_dictionary.json') ## FOR TEST -jwlee
obs_dic = json.loads(fjson.read())
fjson.close()

execfile('../lib/plot_map_4panel.py')

# OBS path
opathin = basedir + 'processed_data/obs/atm/mo/VAR/OBS/ac/VAR_OBS_000001-000012_ac.nc'

# MOD path
#mpathin = '/work/gleckler1/processed_data/metrics_package/interpolated_model_clims_EXP/global/cmip5.MOD.EXP.r1i1p1.mo.Amon.VAR.ver-1.1980-2005.interpolated.linear.2.5x2.5.global.AC.nc'
if exp == 'historical':
  mpathin = '/work/gleckler1/processed_data/cmip5clims_metrics_package-EXP/VAR_MOD_Amon_EXP_r1i1p1_198001-200512-clim.nc'
elif exp == 'amip':
  mpathin = '/work/gleckler1/processed_data/cmip5clims_metrics_package-EXP/VAR_MOD_Amon_EXP_r1i1p1_198101-200512-clim.nc'
elif exp == 'picontrol'
  mpathin = '/work/gleckler1/processed_data/cmip5clims_metrics_package-EXP/VAR_MOD_Amon_EXP_r1i1p1_01-12-clim.nc'

print mpathin

#----------------------------------------------------------------------------
# Log file
import datetime
now = datetime.datetime.now()
if debug:
  LogfileName = 'log.txt'
else:
  LogfileName = 'log_' + str(now.year) + '{0:0=2d}'.format(now.month) + '{0:0=2d}'.format(now.day) + '_' + '{0:0=2d}'.format(now.hour) + '{0:0=2d}'.format(now.minute) + '.txt'
logfile = open(LogfileName, 'w')

# Make output directory
po = plots_outdir
subs = ['',era,exp]
for sub in subs: 
  po = po + '/' + sub
  try:
    os.makedirs(po)
  except:
    pass

##################################################################################
# Variable dictionary
# var_dic[var]
#             ['long_var_name']: full name of variable
#             ['unit_plot']: unit to be plotted
#             ['unit_adjust']: tuple, e.g., (True, multiply, number) or (False, 0, 0)
##################################################################################
tree = lambda: collections.defaultdict(tree)
var_dic = tree()

var_dic = {
  'pr': {
     'var_long_name': 'Precipitation',
     'units_plot': 'mm d-1',
     'units_adjust': (True, 'multiply', 86400.), # 'kg m-2 s-1' to 'mm d-1'
     'obsname': str(obs_dic['pr']['default']),
     'colormap': 'band_12', # 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', # 'bl_to_darkred'
     'isofill': 'AMIP_pr',
     'isofill_mzm': 'pr_anom1_bw1', 
     'isofill_diff': 'pr_anom1_bw1', ## BUT, HARD-CODED!!
     },
  'prw': {
     'var_long_name': 'Atmosphere Water Vapor Content',
     'units_plot': 'kg m-2',
     'units_adjust': (False, 0, 0),
     'obsname': str(obs_dic['prw']['default']),
     'colormap': 'band_12', # 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', # 'bl_to_darkred'
     'isofill': 'AMIP_prw',
     'isofill_mzm': 'pr_anom1_bw1',
     'isofill_diff': 'pr_anom1_bw1', ## BUT, HARD-CODED!!
     },
  'psl': {
     'var_long_name': 'Sea Level Pressure',
     'units_plot': 'hPa',
     'units_adjust': (True, 'divide', 100.), # Pa to hPa
     'obsname': str(obs_dic['psl']['default']),
     'colormap': 'default_1', # 'dvbluered'
     'colormap_diff': 'bl_to_darkred',
     'isofill': 'AMIP_psl',
     'isofill_mzm': 'AMIP_psldif',
     'isofill_diff': 'AMIP_psldif',
     },
  'rltcre': {
     'var_long_name': 'TOA longwave cloud radiative effect',
     'units_plot': 'W m-2',
     'units_adjust': (False, 0, 0),
     'obsname': str(obs_dic['rltcre']['default']),
     'colormap': 'default_1', # 'dvbluered'
     'colormap_diff': 'bl_to_darkred',
     'isofill': 'rlt_clim', ## BUT, HARD-CODED!!
     'isofill_mzm': 'AMIP_rlta',
     'isofill_diff': 'AMIP_rlta',
     },
  'rlut': {
     'var_long_name': 'TOA outgoing longwave radiation',
     'units_plot': 'W m-2',
     'units_adjust': (False, 0, 0),
     'obsname': str(obs_dic['rlut']['default']),
     'colormap': 'default_1', # 'dvbluered'
     'colormap_diff': 'bl_to_darkred',
     'isofill': 'AMIP_rlt',
     'isofill_mzm': 'AMIP_rlta',
     'isofill_diff': 'AMIP_rlta',
     },
  'rstcre': {
     'var_long_name': 'TOA shortwave cloud radiative effect',
     'units_plot': 'W m-2',
     'units_adjust': (False, 0, 0),
     'obsname': str(obs_dic['rltcre']['default']),
     'colormap': 'default_1', # 'dvbluered'
     'colormap_diff': 'bl_to_darkred',
     'isofill': 'AMIP_rls',
     'isofill_mzm': 'AMIP_rlta',
     'isofill_diff': 'AMIP_rlta',
     },
  'tas': {
     'var_long_name': 'Near-Surface Air Temperature',
     'units_plot': 'deg C',
     'units_adjust': (True, 'subtract', 273.15), # 'K' to 'C'
     'obsname': str(obs_dic['tas']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_tas',
     'isofill_mzm': 'AMIP_tasvar',
     'isofill_diff': 'AMIP_tasvar', ## BUT, HARD-CODED!!
     },
  'ta-200': {
     'var_long_name': 'Air Temperature at 200 hPa',
     'units_plot': 'deg C',
     'units_adjust': (True, 'subtract', 273.15), # 'K' to 'C'
     'obsname': str(obs_dic['ta']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_ta200',
     'isofill_mzm': 'AMIP_ta200var',
     'isofill_diff': 'AMIP_ta200var', ## BUT, HARD-CODED!!
     'level': 20000 # Pa
     },
  'ta-850': {
     'var_long_name': 'Air Temperature at 850 hPa',
     'units_plot': 'deg C',
     'units_adjust': (True, 'subtract', 273.15), # 'K' to 'C'
     'obsname': str(obs_dic['ta']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_ta850', ## BUT, HARD-CODED (because of bug in given levels: two 1e20s at the end..)
     'isofill_mzm': 'AMIP_ta850var',
     'isofill_diff': 'AMIP_ta850var', ## BUT, HARD-CODED!!
     'level': 85000 # Pa
     },
  'ua-200': {
     'var_long_name': 'Eastward Wind at 200 hPa',
     'units_plot': 'm s-1',
     'units_adjust': (False, 0, 0),
     'obsname': str(obs_dic['ua']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_u200',
     'isofill_mzm': 'AMIP_u200var',
     'isofill_diff': 'AMIP_u200var', ## BUT, HARD-CODED!!
     'level': 20000 # Pa
     },
  'ua-850': {
     'var_long_name': 'Eastward Wind at 850 hPa',
     'units_plot': 'm s-1',
     'units_adjust': (False, 0, 0), 
     'obsname': str(obs_dic['ua']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_u850', ## BUT, HARD-CODED (because of bug in given levels: two 1e20s at the end..)
     'isofill_mzm': 'AMIP_u850var',
     'isofill_diff': 'AMIP_u200var', ## BUT, HARD-CODED!!
     'level': 85000 # Pa
     },
  'va-200': {
     'var_long_name': 'Northward Wind at 200 hPa',
     'units_plot': 'm s-1',
     'units_adjust': (False, 0, 0),
     'obsname': str(obs_dic['va']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_v200',
     'isofill_mzm': 'AMIP_v200var',
     'isofill_diff': 'AMIP_v200var', ## BUT, HARD-CODED!!
     'level': 20000 # Pa
     },
  'va-850': {
     'var_long_name': 'Northward Wind at 850 hPa',
     'units_plot': 'm s-1',
     'units_adjust': (False, 0, 0), 
     'obsname': str(obs_dic['va']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_v850', ## BUT, HARD-CODED (because of bug in given levels: two 1e20s at the end..)
     'isofill_mzm': 'AMIP_v850var',
     'isofill_diff': 'AMIP_v200var', ## BUT, HARD-CODED!!
     'level': 85000 # Pa
     },
  'zg-500': {
     'var_long_name': 'Geopotential Height',
     'units_plot': 'm',
     'units_adjust': (False, 0, 0),
     'obsname': str(obs_dic['zg']['default']),
     'colormap': 'default_1', # 'band_8', 'default_1', 'dvbluered'
     'colormap_diff': 'band_6', #'bl_to_darkred',
     'isofill': 'AMIP_zg500',
     'isofill_mzm': 'AMIP_zg500var',
     'isofill_diff': 'AMIP_zg500var', ## BUT, HARD-CODED!!?
     'level': 50000 # Pa
     },
   }

vars = sorted(var_dic.keys())

#vars = ['pr']
#vars = ['prw','psl']
#vars = ['rlut', 'rltcre', 'rstcre']
#vars = ['tas', 'ta-200', 'ta-850']
#vars = ['ua-200', 'ua-850', 'va-200', 'va-850']
#vars = ['zg-500']

seasons = ['djf', 'mam', 'jja', 'son']

if debug:
  vars = ['pr']
  seasons = ['djf']

##################################################################################
# Open VCS canvas and load color maps
##################################################################################
print 'setup canvas'
canvas = vcs.init(geometry=(1100,850),bg=1)

# Load Ken's color maps and iso levels
canvas.scriptrun('../lib/initial.attributes_sperber_081617.json')

# Logos for canvas
logo1 = vcs.utils.Logo('../../../../../share/pcmdi/PCMDILogo_200x65px_72dpi.png') # PCMDI
logo2 = vcs.utils.Logo('../../../../../share/pcmdi/CDATLogo_200x70px_72dpi.png') # New CDAT

# Load Karl's color maps
execfile('../lib/taylor_colormaps_stretch.py')

##################################################################################
# LOOP START
##################################################################################
print 'Loop start'
for var in vars:
  var_long_name = var_dic[var]['var_long_name']

  if RemoveZonalMean is True: var_long_name = var_long_name + ""

  if RemoveZonalMean or RemoveAnnualMean:
    var_dic[var]['isofill'] = var_dic[var]['isofill_mzm']

  #==============================================================================
  # Observation
  #------------------------------------------------------------------------------
  obsd = var_dic[var]['obsname'] 

  if 'level' in var_dic[var]:
    var_shortname = var.split('-')[0]
    obst = string.replace(opathin,'VAR',var_shortname)
  else:
    obst = string.replace(opathin,'VAR',var)

  obst = string.replace(obst,'OBS',obsd)
  fo = cdms2.open(obst)

  if 'level' in var_dic[var]:
    level = var_dic[var]['level']
    do = fo(var_shortname, longitude=(0,360), latitude=(-90,90), level=level)
  else:
    do = fo(var, longitude=(0,360), latitude=(-90,90))

  cdutil.setTimeBoundsMonthly(do)

  fo.close()

  # Missing data maskout (temporary, for special case: prw, RSS, no data over land nor ice)
  if var == 'prw':
    do_masked = MV2.masked_where(MV2.equal(do,0.0),do)
    do_masked.setAxisList(do.getAxisList()) 
    do = do_masked

  ogrid = do.getGrid()

  # Adjust Units
  if var_dic[var]['units_adjust'][0]:
    operator = var_dic[var]['units_adjust'][1]
    number = var_dic[var]['units_adjust'][2]
    do = getattr(MV2,operator)(do, number)

  # Seasonal climatology of observation
  obs = {}
  for season in seasons:

    obs[season] = pcmdi_metrics.pcmdi.seasonal_mean.compute(do,season)

    if RemoveZonalMean:
      obs[season] = remove_zonal_mean(obs[season])

    if RemoveAnnualMean:
      obs[season] = remove_annual_mean(obs[season], do)

  #==============================================================================
  # Models
  #------------------------------------------------------------------------------
  # Gest list of models
  mods = []

  mpatht = string.replace(mpathin,'MOD','*')
  mpatht = string.replace(mpatht,'VAR',var)
  mpatht = string.replace(mpatht,'EXP',exp)

  lst = os.popen('ls ' + mpatht).readlines()
  for l in lst:
    mod = string.split(l,'/')[-1].split('_')[1]
    if mod not in mods: mods.append(mod)

  mods = sorted(mods)

  if debug:
    mods = mods[0:3] # FOR TEST -jwlee
    mods = mods[0:1] # FOR TEST -jwlee

  # Dictionary for save fields
  fld = {} # Model's climatology field
  dif = {} # Difference btw. model and obs
  mmm = {} # Multi model ensemble mean (MMM)
  mmm_dif = {} # MMM - OBS
  mgrid = {}

  #------------------------------------------------------------------------------
  # Calculate seasonal mean and its difference against obs from MMM and individual models 
  #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  for mod in mods:
    fld[mod] = {} # Model's climatology field
    dif[mod] = {} # Difference btw. model and obs
    mgrid[mod] = {} # Model's grid (dependent to model input file)

  for season in seasons:
    mmm[season] = 0

    time1 = time.time() # Time checker

    for mod in mods:

      mpatht = string.replace(mpathin,'MOD',mod)
      mpatht = string.replace(mpatht,'VAR',var)
      mpatht = string.replace(mpatht,'EXP',exp)

      fm = cdms2.open(mpatht)

      if 'level' in var_dic[var]:
        dm = fm(var_shortname, longitude=(0,360), latitude=(-90,90), level=level)
      else:
        dm = fm(var, longitude=(0,360), latitude=(-90,90))

      # Adjust units
      if var_dic[var]['units_adjust'][0]:
        dm = getattr(MV2,operator)(dm, number)

      cdutil.setTimeBoundsMonthly(dm)

      fm.close()

      #print 'calc', var, season, mod

      #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
      # Interpolation handlings.......
      #...........................................................................
      # Model input grid
      if season == seasons[0]:
        mgrid[mod] = dm.getGrid()

        # If obs has higher resolution than model AND all models already have been processed to have same grid
        if mod == mods[0]:
          if OgridAsCommon:
            refgrid = ogrid
          else:
            refgrid = mgrid[mod]

      if mod == mods[0]:
        if OgridAsCommon:
          obs_season_regrid = obs[season]
        else:
          obs_season_regrid = obs[season].regrid(refgrid, regridTool='regrid2', mkCyclic=True)
      #...........................................................................

      # Seasonal climatology
      fld[mod][season] = pcmdi_metrics.pcmdi.seasonal_mean.compute(dm,season)

      # Zonal Mean Remove?
      if RemoveZonalMean:
        fld[mod][season] = remove_zonal_mean(fld[mod][season])

      # Annual Mean Remove?
      if RemoveAnnualMean:
        fld[mod][season] = remove_annual_mean(fld[mod][season], dm)

      # Regrid to observational grid
      fld_regrid = fld[mod][season].regrid(refgrid, regridTool='regrid2', mkCyclic=True)

      # Accumulate for MMM
      mmm[season] = MV2.add(mmm[season], fld_regrid)

      # Get difference field
      dif[mod][season] = MV2.subtract(fld_regrid, obs_season_regrid)
      dif[mod][season].id = 'Diff_'+season.upper()+'_'+var

    # Get multi-model mean (MMM)
    mmm[season] = MV2.divide(mmm[season],float(len(mods)))

    # MMM - OBS for each season
    mmm_dif[season] = MV2.subtract(mmm[season], obs_season_regrid)
    mmm_dif[season].id = 'Diff_'+season.upper()+'_'+var

    time2 = time.time() # Time checker
    timec = time2 - time1

    print 'MMM', var, season, timec
    logfile.write('MMM'+' '+var+' '+season+' '+str(timec)+'\n')

  #------------------------------------------------------------------------------
  # Create 4 panel plots: model, obs, model-obs, mmm-obs
  #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  pout = plots_outdir + '/' + era + '/' + exp + '/' + odir + '/' + var

  try:
    os.makedirs(pout)
  except:
    pass

  for mod in mods:
    for season in seasons:
      output_file_name = pout + '/' + var + '.' + mod + '_' + season

      units = var_dic[var]['units_plot']

      time1 = time.time() # Time checker

      plot_4panel(canvas, logo1, logo2,
                  var_dic,
                  var, var_long_name, units, season, 
                  mod, 
                  fld[mod][season], obs[season], 
                  dif[mod][season], mmm_dif[season], 
                  output_file_name, option)

      time2 = time.time() # Time checker
      timec = time2 - time1
      
      print 'plot', var, mod, season, timec
      logfile.write('plot '+var+' '+mod+' '+season+' '+str(timec)+'\n')

canvas.close()
