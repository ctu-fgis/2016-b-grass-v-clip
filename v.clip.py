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

#%option G_OPT_V_INPUTS
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
#% description: dissolve
#%end

# DOTAZY
# ma byt vstup pouze pro jednu vrstvu, nebo pro vic?
# ma byt vystupem nova vrstva, nebo clipla stara vrstva?
# error - input layer - AREA, LINIE, ne POINT (to nedava smysl)
# error - clip layer - AREA, ne POINT, LINE (to dava smysl)

# TODO - podpora pouze linie plochy, ne mix s body, pouze body =>select
# body + dissolve =>ignorovat dissolve, select+overlap

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
   
    # do maps exist?
    if not grass.find_file(input_map, element='vector')['file']:
        grass.fatal(_("Vector map <%s> not found") % input_map)
    elif not grass.find_file(clip_map, element='vector')['file']:
        grass.fatal(_("Vector map <%s> not found") % clip_map)
    else:
        # TODO - layer numbers?
        try:
            clip(input_map, clip_map, output_map)
        except  CalledModuleError as e:
            grass.fatal(_("Clipping steps failed."
                          " Check above error messages and"
                          " see following details:\n%s") % e)
    # write cmd history:
    grass.vector_history(output)
    
def clip(input_data, clip_data, out_data):
    grass.run_command('v.overlay', ainput = input_data, binput = clip_data, operator = 'and', output = out_data, olayer = '0,1,0')
  

if __name__ == "__main__":
    opt, flg = parser() 
    main()
    
  


