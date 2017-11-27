import EzTemplate
import vcs  
import time

#===========================================================================================
def plot_4panel(canvas, 
                var_dic,
                var, var_long_name, units, season, model, s1, s2, s3, s4, output_file_name, option):
#-------------------------------------------------------------------------------------------
  ## Input fields ---
  s = []
  s.append(s1)
  s.append(s2)
  s.append(s3)
  s.append(s4)

  ## Canvas --
  canvas.clear()
  canvas.drawlogooff() # Trun off old UVCDAT logo

  ## iso setup ---
  iso = canvas.getisofill(var_dic[var]['isofill'])
  iso = setup_iso(var, iso, var_dic, diff=False)

  iso_diff = canvas.getisofill(var_dic[var]['isofill_diff'])
  iso_diff = setup_iso(var, iso_diff, var_dic, diff=True)

  # Increase label text size ---
  my_template = vcs.createtemplate()
  my_template,txt = label_setup(my_template)

  # Title on top ---
  plot_title = vcs.createtext()
  plot_title.x = .5
  plot_title.y = .975
  plot_title.height = 30
  plot_title.halign = 'center'
  plot_title.valign = 'top'
  plot_title.color = 'black'

  titadd = ''
  if option == 2: titadd = ' dev from zonal mean'
  if option == 3: titadd = ' dev from annual mean'

  plot_title.string = var_long_name + ': ' + season.upper() + titadd
  canvas.plot(plot_title)

  plot_title.y = .935
  plot_title.height = 20
  plot_title.string = '('+era.upper()+' '+exp+': 1980-2005)'
  canvas.plot(plot_title)

  templates = []

  ## EzTemplate ---
  M = EzTemplate.Multi(template=my_template, rows=2,columns=2, x=canvas)  
  
  # Legend colorbar ---
  M.legend.thickness = 0.4 # Thickness of legend color bar
  M.legend.direction = 'horizontal' 
  
  # Border margin for entire canvas ---
  #M.margins.top = .14
  M.margins.top = .16
  #M.margins.bottom = .09
  M.margins.bottom = .11
  M.margins.left = .05  
  M.margins.right = .05  
  
  # Interval spacing between subplots ---
  M.spacing.horizontal = .05
  M.spacing.vertical = .10
  
  # Plot subplots ---
  left_pos = 0
  for i in range(4):  
    if i==0:
      r=0
      c=0
    elif i==1:
      r=0
      c=1
    elif i==2:
      r=1
      c=0
    else:
      r=1
      c=1
    t = M.get(legend='local',row = r, column = c) # Use local colorbar
    templates.append(t)
    if i%2 !=1:  
      t.legend.priority=0 # Turn off legend  
      left_pos = t.data.x1
    else:
      # Set legend (colorbar) position
      t.legend.x1 = left_pos
      t.legend.x2 = t.data.x2
      t.legend.y1 = t.legend.y1 - 0.04
      t.legend.y2 = t.legend.y2 - 0.04
  
    t = setup_template(t)
  
    if i < 2: 
      canvas.plot(s[i], t, iso)
    else:
      canvas.plot(s[i], t, iso_diff)
  
    # Titles of subplots ---
    plot_title.height = 20
    if i == 0: 
      plot_title.string = model # multi-realization mean...?
      plot_title.x = .27
      #plot_title.y = .92
      plot_title.y = .90
    elif i == 1: 
      plot_title.string = var_dic[var]['obsname'] + ' (OBS)'
      plot_title.x = .73
      #plot_title.y = .92
      plot_title.y = .90
    elif i == 2: 
      plot_title.string = model+' - ' + var_dic[var]['obsname']
      plot_title.x = .27
      plot_title.y = .48
    elif i == 3: 
      plot_title.string = 'MMM - ' + var_dic[var]['obsname']
      plot_title.x = .73
      plot_title.y = .48
    canvas.plot(plot_title)

  del(M)

  # Units ---
  plot_title.string = '['+units+']'
  plot_title.height = 17

  plot_title.x = .90
  plot_title.y = .49
  canvas.plot(plot_title) # next to top colorbar

  plot_title.x = .90
  plot_title.y = .075
  canvas.plot(plot_title) # next to bottom colorbar

  # Logos ---
  # PCMDI
  #logo2 = vcs.utils.Logo('/work/lee1043/cdat/pmp/mean_climate_maps/lib/160915_PCMDI_logo-oblong_377x300px.png')
  logo2 = vcs.utils.Logo('/work/lee1043/cdat/pmp/mean_climate_maps/lib/PCMDILogo_200x65px_72dpi.png')
  #logo2.x = .06
  logo2.x = .9
  #logo2.y = .03
  logo2.y = .96
  #logo2.width = logo2.source_width * .3
  #logo2.height = logo2.source_height * .3
  logo2.width = logo2.source_width
  logo2.height = logo2.source_height
  logo2.plot(canvas)

  # LLNL
  #logo3 = vcs.utils.Logo('/work/lee1043/cdat/pmp/mean_climate_maps/lib/LLNL-logo.png')
  #logo3.x = .11
  #logo3.y = .03
  #logo3.width = logo2.source_width * .6
  #logo3.height = logo2.source_height * .6
  #logo3.plot(canvas)

  # New CDAT
  logo_CDAT = vcs.utils.Logo('../lib/171101_doutriaux1_CDATLogo_1707x878px-300dpi.jpg')
  logo_CDAT.x = .06
  logo_CDAT.y = .018
  logo_CDAT.width = logo_CDAT.source_width * .08
  logo_CDAT.height = logo_CDAT.source_height * .08
  logo_CDAT.plot(canvas)
  
   
  #-------------------------------------------------
  # Drop output as image file (--- vector image?)
  #- - - - - - - - - - - - - - - - - - - - - - - - - 
  time.sleep(0.1)

  canvas.png(output_file_name+'.png')

  canvas.clear()
  canvas.removeobject(my_template)
  canvas.removeobject(plot_title)
  for t in templates:
      canvas.removeobject(t)
  for t in txt:
      canvas.removeobject(t)

#===========================================================================================
def setup_template(t):
#-------------------------------------------------------------------------------------------
  # Turn off no-needed information -- prevent overlap
  t.blank(['title','dataname','crdate','crtime', # 'mean','min','max'
           'units','zvalue','tvalue','xunits','yunits','xname','yname'])
  return(t)

#===========================================================================================
def setup_iso(var, iso, var_dic, diff):
#-------------------------------------------------------------------------------------------
  # Customize color ---
  if not diff: 
    iso.colormap = var_dic[var]['colormap'] 
  else:
    iso.colormap = var_dic[var]['colormap_diff']

  #iso.boxfill_type = 'custom'

  if diff:
    if var == 'pr':
      iso.levels = [-1.e20, -5, -2, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 2, 5, 1.e20]
    elif var == 'prw':
      iso.levels = [-1.e20, -10, -5, -2, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 2, 5, 10, 1.e20]
    elif var in ['tas', 'ta-200', 'ta-850']:
      iso.levels = [-1.e20, -15, -10, -5, -2, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 2, 5, 10, 15, 1.e20]
    elif var in ['ua-200',  'ua-850', 'va-200', 'va-850']:
      iso.levels = [-1.e20, -25, -20, -15, -10, -5, -2, 0, 2, 5, 10, 15, 20, 25, 1.e20]
    elif var == 'zg-500':
      iso.levels = range(-120, 140, 20)
      iso.levels.insert(0, -1.e20)
      iso.levels.append(1.e20)
    elif var == 'ta-850':
      iso.levels = range(-6, 8, 2)
      iso.levels.insert(0, -1.e20)
      iso.levels.append(1.e20)
    elif var in ['ua-850', 'va-850', 'va-200', 'psl']:
      iso.levels = range(-10, 12, 2)
      iso.levels.insert(0, -1.e20)
      iso.levels.append(1.e20)
  else:
    if var == 'rltcre':
      iso.levels = range(-25,30,5)  #range(0,100,10)
      iso.levels.insert(0, -1.e20)
      iso.levels.append(1.e20)
    if var == 'ta-850':
      iso.levels = range(-35,40,5)
      iso.levels.insert(0, -1.e20)
      iso.levels.append(1.e20)
    if var == 'ua-850':
      iso.levels = range(-25,30,5)
      iso.levels.insert(0, -1.e20)
      iso.levels.append(1.e20)
    if var == 'va-850':
      iso.levels = range(-10,14,2)
      iso.levels.insert(0, -1.e20)
      iso.levels.append(1.e20)

  if type(iso.levels[0]) is list:
    lmax = max(iso.levels)[1]
    lmin = min(iso.levels)[0]
  else:
    lmax = max(iso.levels)
    lmin = min(iso.levels)

  if lmax > 0 and lmin < 0: 
    colors = vcs.getcolors(iso.levels,colors=range(16,240),split=0)
  else:
    colors = vcs.getcolors(iso.levels,colors=range(16,240))

  if diff and var == 'pr':
    colors.reverse()

  iso.fillareacolors = colors

  iso.missing = 0 # Set missing value color as same as background
  iso.missing = 'white' # Set missing value color as same as background

  # Plot label control (latitude and longitude)
  iso.xticlabels('','')
  iso.yticlabels('','')
  iso.xticlabels1 = {60:'60E', 120:'120E', 180:'180W', 240:'120W', 300:'60W'} 
  iso.yticlabels1 = { -80:'80S', -60:'60S', -40:'40S', -20:'20S', 0:'EQ', 20:'20N', 40:'40N', 60:'60N', 80:'80N'}

  # Colorbar labels
  '''
  iso.level could be either:
    - [[-1e+20, 0.1], [0.1, 0.2], ..., [20.0, 30.0], [30.0, 1e+20]], or
    - [-5, -2, -1, -0.5, -0.2, 0, 0.2, 0.5, 1, 2, 5]
  Below is for eleminating unessasry precision for colorbar labels. (e.g., 3.0 --> 3)
  '''
  legendlabels = {}
  for x in iso.levels: # e.g. x could be either [-1e+20, 0.1] or -5

    if type(x) is list:
      x1 = float(x[1])
    else:
      x1 = float(x)
    
    if x1.is_integer():
      legendlabels[x1] = str(int(x1))
    else:
      legendlabels[x1] = str(x1)

  iso.legend = legendlabels

  return(iso)

#===========================================================================================
def label_setup(my_template):
#-------------------------------------------------------------------------------------------
  tick_text = vcs.createtext()
  tick_text.height = 16
  tick_text.valign = "half"
  tick_text.halign = "center"
  my_template.xlabel1.textorientation = tick_text.To_name
  my_template.xlabel1.texttable = tick_text.Tt_name

  tick_text2 = vcs.createtext()
  tick_text2.height = 16
  tick_text2.valign = "half"
  tick_text2.halign = "right"
  my_template.ylabel1.textorientation = tick_text2.To_name
  my_template.ylabel1.texttable = tick_text2.Tt_name

  tick_text3 = vcs.createtext()
  tick_text3.height = 23
  tick_text3.valign = "half"
  tick_text3.halign = "center"
  my_template.legend.textorientation = tick_text3.To_name
  my_template.legend.texttable = tick_text3.Tt_name

  return(my_template, [tick_text,tick_text2,tick_text3])
