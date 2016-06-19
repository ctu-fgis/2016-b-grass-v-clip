#!/usr/bin/env python

############################################################################
#
# MODULE:       v.clip
# AUTHOR:       Zofie Cimburova, CTU Prague, Czech Republic
# PURPOSE:      Clips vector features
# COPYRIGHT:    (C) 2016 Zofie Cimburova
#               This program is free software under the GNU General
#               Public License (>=v2). Read the file COPYING that
#               comes with GRASS for details.
#
#############################################################################

#%module
#% description: Extracts features of input map(s) which overlay features of clip map.
#% keyword: vector
#% keyword: clip
#% keyword: area
#% keyword: 
#%end

#%option G_OPT_V_INPUT
#% key: input
#% label: Name of vector map to be clipped
#%end

#%option G_OPT_V_INPUT
#% key: clip
#% label: Name of clip vector map
#%end

#%option G_OPT_V_OUTPUT
#% key: output
#% label: Name of output vector map
#%end

#%flag
#% key: d
#% description: Dissolve clip map
#%end

#%flag
#% key: r
#% description: Clip by region
#%end

# TODO - nepridava se vysledna mapa do seznamu vrstev
# TODO - nemuze byt zaroven -d a -r

# TODO - co z tohohle muzu smazat?
from grass.script import run_command, message, percent, parser
import os
import sys
import datetime
import grass.script as grass
from grass.exceptions import CalledModuleError

def main():
    input_map  = opt['input']
    clip_map   = opt['clip']
    output_map = opt['output']
    
    flag_dissolve = flg['d']
    flag_region   = flg['r']
    
  
    # ---- clip with dissolve ---- #
    # TODO - Martin - dissolve without input column
    if (flag_dissolve):
        grass.message("Flag - dissolve")

        # setup temporary file
        temp_clip_map = '%s_%s' % ("temp", str(os.getpid()))
        
        # dissolve clip_map
        grass.run_command('v.dissolve', input = clip_map, output = temp_clip_map)
        grass.message(temp_clip_map)
        
        # perform clipping
        clip(input_map, temp_clip_map, output_map)
        
        # delete temporary file
        grass.run_command('g.remove', flags='f', type='vector', name=temp_clip_map)
    
    
     # ---- clip by region ---- #
     # TODO - disable clip layer option?
    if (flag_region):
        grass.message("Flag - region")
        
        # setup temporary file
        temp_region_map = '%s_%s' % ("temp", str(os.getpid()))
        
        # create a map covering current computational region
        grass.run_command('v.in.region', output = temp_region_map)
        grass.message(temp_region_map)
        
        # perform clipping
        clip(input_map, temp_region_map, output_map)
        
        # delete temporary file
        grass.run_command('g.remove', flags='f', type='vector', name=temp_region_map)
       
    
    
    # ---- dissolve clippingn map ---- #
    else: 
        grass.message("No flag")

        # perform clippings
        clip(input_map, clip_map, output_map)
    
        # write cmd history:
        grass.vector_history(output_map)
    
def clip(input_data, clip_data, out_data):
    try:
        grass.message("before clipping")
        grass.run_command('v.overlay', ainput = input_data, binput = clip_data, operator = 'and', output = out_data, olayer = '0,1,0')
        grass.message("after clipping")
    except  CalledModuleError as e:
        grass.fatal(_("Clipping steps failed."
                    " Check above error messages and"
                    " see following details:\n%s") % e)


if __name__ == "__main__":
    opt, flg = parser() 
    main()
    
  


