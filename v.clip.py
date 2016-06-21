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
#% description: Extracts features of input map which overlay features of clip map.
#% keyword: vector
#% keyword: clip
#% keyword: area
#%end

#%option G_OPT_V_INPUT
#% label: Name of vector map to be clipped
#%end

#%option G_OPT_V_INPUT
#% key: clip
#% label: Name of clip vector map
#%end

#%option G_OPT_V_OUTPUT
#%end

#%flag
#% key: d
#% description: Dissolve clip map
#%end

#%flag
#% key: r
#% description: Clip by region
#% suppress_required: yes
#%end

# TODO - nepridava se vysledna mapa do seznamu vrstev
# TODO - nemuze byt zaroven -d a -r => igonorovat -d pokud -r
### -> https://grass.osgeo.org/grass73/manuals/g.parser.html
# TODO - chyby pri spusteni - nekdy, po opakovanem spusteni bez chyby (?)
# TODO - jak zachazet s temp mapou

import os
import atexit

from grass.script import run_command, message, parser
import grass.script as grass
from grass.exceptions import CalledModuleError

TMP = []

def cleanup():
    for name in TMP:
        grass.run_command('g.remove', flags='f', type='vector', name=name)

def main():
    input_map  = opt['input']
    clip_map   = opt['clip']
    output_map = opt['output']
    
    flag_dissolve = flg['d']
    flag_region   = flg['r']
    
    # ======================================== #
    # ========== INPUT MAP TOPOLOGY ========== #
    # ======================================== #
    vinfo = grass.vector_info_topo(input_map)
    lines_count = vinfo['lines']
    points_count = vinfo['points']
    areas_count = vinfo['areas']
    grass.debug("There are {0} lines, {1} points and {2} areas".format(lines_count, points_count, areas_count), 1)
    
    # ==== only points ==== #
    if (points_count > 0 and lines_count == 0 and areas_count == 0):
        
        # ==================================== #
        # ========== CLIP BY REGION ========== #
        # ==================================== #
        if (flag_region):
            clip_r(input_map, output_map, clip_s)

        # ================================= #
        # ========== NORMAL CLIP ========== #
        # ================================= #
        else:
            grass.message("Clipping by clip map.")
            # perform clipping
            clip_s(input_map, clip_map, output_map)
                
    # ==== lines, areas, lines + areas ==== #
    # ==== points + areas, points + lines, points + areas + lines ==== #
    else:
        if (points_count > 0):
            grass.warning("Input map contains multiple geometry, only lines and areas will be clipped.")
    
        # ==================================== #
        # ========== CLIP BY REGION ========== #
        # ==================================== #
        # TODO - disable clip layer option?
        if (flag_region):
            clip_r(input_map, output_map, clip_o)
        
        # ======================================== #
        # ========== CLIP WITH DISSOLVE ========== #
        # ======================================== #
        # TODO - Martin - dissolve without input column
        elif (flag_dissolve):
            grass.message("Clipping by dissolved clip map.")

            # setup temporary file
            temp_clip_map = '%s_%s' % ("temp", str(os.getpid()))
            
            # dissolve clip_map
            grass.run_command('v.dissolve', input = clip_map, output = temp_clip_map)
            
            # perform clipping
            clip_o(input_map, temp_clip_map, output_map)
            
            # delete temporary file
            grass.run_command('g.remove', flags='f', type='vector', name=temp_clip_map)
        
        # ================================= #
        # ========== NORMAL CLIP ========== #
        # ================================= #
        else: 
            grass.message("Clipping by clip map.")

            # perform clippings
            clip_o(input_map, clip_map, output_map)
        
def clip_r(input_map, output_map, clip_fn):
    grass.message("Clipping by region.")

    # setup temporary map
    temp_region_map = '%s_%s' % ("temp", str(os.getpid()))
    TMP.append(temp_region_map)

    # create a map covering current computational region
    grass.run_command('v.in.region', output = temp_region_map)

    # perform clipping
    clip_fn(input_map, temp_region_map, output_map)

        
def clip_o(input_data, clip_data, out_data):
    try:
        grass.run_command('v.overlay', ainput = input_data, binput = clip_data, operator = 'and', output = out_data, olayer = '0,1,0')

    except  CalledModuleError as e:
        grass.fatal(_("Clipping steps failed."
                    " Check above error messages and"
                    " see following details:\n%s") % e)
                    
                    
def clip_s(input_data, clip_data, out_data):
    try:
        grass.run_command('v.select', ainput = input_data, binput = clip_data, output = out_data, operator = 'overlap')
    
    except  CalledModuleError as e:
        grass.fatal(_("Clipping steps failed."
                    " Check above error messages and"
                    " see following details:\n%s") % e)

if __name__ == "__main__":
    atexit.register(cleanup)
    opt, flg = parser()
    main()
    
  


