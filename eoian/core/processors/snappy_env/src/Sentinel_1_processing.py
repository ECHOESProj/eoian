'''
Name: Sentinel 1 Pre-processing Script
 
Description: Processes raw Sentinel-1 SAR data, outputting corrected data for analysis. This script is automated and will process 
             all data within the hosting folder.

Minimum Requirements: os, sys, snappy_env, matplotlib, shutil.

Inputs: 1 Sentinel zipped data folder (Automative Process)

Outputs: 1 data folder & 1 SNAP.dim file

Author: Caoimhin Kelly

Created: 11/02/2021
'''

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

# Declare required Snappy modules
import os
from os import walk
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
import shutil, os, glob

def do_terrain_correction(source):
    # Terrain correction corrects geometric distortions that lead to geolocation errors.
    
    # A new set of Paramters are created with dem Name selected as SRTM 3Sec and Reampling method are Bilinear. 
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    #proj = '''PROJCS["UTM Zone 4 / World Geodetic System 1984",GEOGCS["World Geodetic System 1984",DATUM["World Geodetic System 1984",SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]],UNIT["degree", 0.017453292519943295],AXIS["Geodetic longitude", EAST],AXIS["Geodetic latitude", NORTH]],PROJECTION["Transverse_Mercator"],PARAMETER["central_meridian", -159.0],PARAMETER["latitude_of_origin", 0.0],PARAMETER["scale_factor", 0.9996],PARAMETER["false_easting", 500000.0],PARAMETER["false_northing", 0.0],UNIT["m", 1.0],AXIS["Easting", EAST],AXIS["Northing", NORTH]]'''
    #parameters.put('mapProjection', proj)       # comment this line if no need to convert to UTM/WGS84, default is WGS84
    #parameters.put('saveProjectedLocalIncidenceAngle', True)
    #parameters.put('saveSelectedSourceBand', True)
    #parameters.put('pixelSpacingInMeter', 40.0)
    ## A new product consisting of the correction is created.
    output = GPF.createProduct('Terrain-Correction', parameters, source)
    
    return output

def do_speckle_filtering(source):
    # Speckle filtering removes granular noise from the data due to the interference of waves reflected from many elementary scatterers.

    # Define a new set of parameters. Note filter type must be set to Lee
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('filter', 'Lee')
    parameters.put('filterSizeX', 5)
    parameters.put('filterSizeY', 5)
    # A new speckle free product is created.
    output = GPF.createProduct('Speckle-Filter', parameters, source)
    
    return output

def do_calibration(source):
    # Calibration provides imagery where pixel values directly relate to the radar backscatter of the scene. 

    # Define a new set of parameters. Note Source band is the Intensity VV band
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    parameters.put('sourceBands', 'Intensity_VV')
    pols = 'VV'
    parameters.put('selectedPolarisations', pols)
    parameters.put('outputImageScaleInDb', False)
    # A new calibrated product is created.
    output = GPF.createProduct("Calibration", parameters, source)
    
    return output

def thermal_noise_removal(source):
    # Thermal noise removes noise and normalizes the signal of the backscatter

    # Define a new set of parameters.
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('removeThermalNoise', True)
    # A new product is created.
    output = GPF.createProduct('ThermalNoiseRemoval', parameters, source)
    return output

def orbitfile(subset):
    # The orbit file provides an accurate position of SAR image and the update of the original metadata of SAR product

    # Define a new set of parameters. 
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    # A new product is created.
    orbit = GPF.createProduct("Apply-Orbit-File", parameters, subset)

    return orbit

def subset_dim(product):

        # Return a type object for the given, fully qualified Java type name which is the name of a Java primitive type, a Java class name, or a Java array type name.
        SubsetOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')

        # Read the WKT of the site boundary as a geom
        wkt = "MULTIPOLYGON(((-6.60903408269214 52.2886335614214,-6.60751865168286 52.4021902868048,-6.34240241567041 52.4067365798326,-6.34391784667969 52.2931798544492,-6.60903408269214 52.2886335614214)))"
        geom = WKTReader().read(wkt)

        op = SubsetOp()
        # Set the Source Product
        op.setSourceProduct(product)
        # Set the Subset Region
        op.setGeoRegion(geom)
        # Copy the Metadata from the raw data
        op.setCopyMetadata(True)
        # Subset the site from the image
        sub_product = op.getTargetProduct()
        
        return sub_product

def raw_processing(Input,Output,filename):
    # This function pulls together all required pre-processing steps for creating a ready to use Sentinel-1 image

    # Input file is read into the process
    product = ProductIO.readProduct(Input)

    # Raw image is subsetted
    subset = subset_dim(product)

    # An Orbit file is attached to the subsetted data
    orbit = orbitfile(subset)

    # Themral Noise is removed from data
    TNR_set = thermal_noise_removal(orbit)

    # Calibration is carried out
    calibrated = do_calibration(TNR_set)

    # Any reflected speckle is removed
    speckled = do_speckle_filtering(calibrated)

    # Terrain correction is applied
    corrected_product = do_terrain_correction(speckled)

    # A .dim file is wrote to folder of the new processed data.
    output_path1 = os.path.join(Output, filename + '_processed.dim')
    print("output_path", output_path1)
    ProductIO.writeProduct(corrected_product, output_path1, 'BEAM-DIMAP')


def RunAll(Input_location, Output_location):
    ## This function seeks all .zip files in the input location and reads in raw data for processing

    for filePath in glob.glob(os.path.join(Input_location, "*.zip")):
       # File name is seperated from input location
       path, filename = os.path.split(filePath) 
       filename = os.path.splitext(filename)[0]
       # Input and Output parameters are defined
       Output = Output_location
       Input = filePath
       # Try clause begins the processing steps
       try:
           raw_processing(Input,Output,filename)
       except:
           print("File:", filename,"didnt work please check")

    print("ran")

def main():
    # Declare input and output location
    Input_location = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\Ireland\Sentinel-1\Repo\SNAP_test"
    Output_location = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\Ireland\Sentinel-1\Repo\SNAP_test\output"

    # Function to run the file reading loop and execute processing
    RunAll(Input_location, Output_location)

if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")