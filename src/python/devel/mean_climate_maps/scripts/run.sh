#python ./mk_clim_dif_maps-driver_4panel.py -e historical -o 1 -d True --outdir ./test1

for exp in 'historical' 'amip' 'picontrol'; do
  for option in '1' '2' '3'; do
    python ./mk_clim_dif_maps-driver_4panel.py -e $exp -o $option \
           --outdir /work/lee1043/cdat/pmp/clim_plots >& log.$exp-$option &
    disown
  done;
done;
