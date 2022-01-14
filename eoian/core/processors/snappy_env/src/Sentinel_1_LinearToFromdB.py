'''
Name: Sentinel 1 Linear to/from dB Script
 
Description: Reads in averaged pixel band and creates a Linear decimal band. This new band is used in a BandMaths calculation to retrieve
             a specific range from the band. The final output is a Geotiff file consisting of the calculated range.

Minimum Requirements: os, sys, snappy_env, matplotlib, shutil.

Inputs: 1 SNAP.dim file

Outputs: 1 Geotiff image

Author: Caoimhin Kelly

Created: 11/02/2021
'''

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

# Declare required Snappy modules
import os
import numpy
import sys
import snappy
from snappy import Product
from snappy import ProductData
from snappy import ProductIO
from snappy import ProductUtils
from snappy import FlagCoding
from snappy import  WKTReader
from snappy import jpy, GPF
import matplotlib.pyplot as plt
from os import walk
import shutil, os, glob
from snappy import PixelPos, GeoPos

def query_product(Input_location,output,query):

    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap() 
    # Return the Band Math object
    BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    targetBand = BandDescriptor()
    targetBand.name = 'Sigma0_db'
    targetBand.type = 'float32'
    # Insert the calculation for extracted pixel values
    targetBand.expression = query
    # Create an array of the pixels from the calcuations
    targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    targetBands[0] = targetBand
    # Store these new pixels as a pair
    parameters.put('targetBands', targetBands)
    # Create the new product of the segmented pixels
    product3 = GPF.createProduct('BandMaths', parameters, output)
    # Create the path for the export of the new image
    path_collocated = os.path.join(Input_location, 'output_linear1_water_sgement.tif')
    # Write the new dataset as a GeoTIFF
    ProductIO.writeProduct(product3, path_collocated, 'GeoTIFF')

    print('GeoTiff has been created')

def convert_to_Linear(Input_location,Input_file):

    # Product is read into script
    Input = os.path.join(Input_location, Input_file)
    product = ProductIO.readProduct(Input)

    # New Parameters are created, the source band is select for the conversion
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_VV')
    output = GPF.createProduct("LinearToFromdB", parameters, product)
    
    # The .dim file is exported 
    output_path1 = os.path.join(Input_location, 'output_linear1.dim')
    print("output_path", output_path1)
    ProductIO.writeProduct(output, output_path1, 'BEAM-DIMAP')

    return output

def m_getPixelPos(Input_location,Input_file,lat,lon):

    from snappy import GeoPos,PixelPos
    import numpy as np

    Input = os.path.join(Input_location, Input_file)
    source = ProductIO.readProduct(Input)
    iwv = source.getBand('Sigma0_VV')

    if source.getSceneGeoCoding().canGetPixelPos() is False:
        raise Exception('Can''t get Pixel Position from this source')
    else:
        pos = GeoPos(lat, lon)

        pixpos=source.getSceneGeoCoding().getPixelPos(pos,None)
        X = np.round(pixpos.getX()) 
        Y = np.round(pixpos.getY())
        print(iwv.getPixels(X, Y))
    return [X,Y]

def main(input_file):
    
    # Declare input and output location
    Input_location = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\Ireland\Sentinel-1\Repo\SNAP_test\output"
    Input_file = 'S1A_IW_GRDH_1SDV_20200915T181432_20200915T181457_034373_03FF3E_ADC0_processed.dim'
    query = 'if Sigma0_VV_db <= -17.183838 theN 1 else 0'

    # Converts the outputted average band to a db band
    output = convert_to_Linear(Input_location,Input_file)

    lat = 52.368061
    lon = -6.420654

    coords = m_getPixelPos(Input_location,Input_file,lat,lon)

    # Performs a query on the newly converted db file
    #query_product(Input_location,output,query)
   
if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    Input = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\Ireland\Sentinel-2\Repo\S2B_MSIL2A_20201106T114349_N0214_R123_T29UPU_20201106T132455.zip"
    main(Input)
    print ("Done!")

