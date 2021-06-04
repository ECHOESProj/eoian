'''
Name: Sentinel 1 Stack Building & Averaging Script
 
Description: Ingests processed Sentinel 1 data creating a single stack product consisting of a specific band from the input data.
             Inputs are held in a list before being inserted into new product. To create a full stack this script is automated to 
             find all processed .dim files in host folder. Once the stack is created the final step calcualtes the average pixel values 
             for all bands in the product.

Minimum Requirements: os, sys, snappy_env, matplotlib, shutil.

Inputs: 1 SNAP.dim file (Automative Process)

Outputs: 1 data folder, 1 SNAP.dim file

Author: Caoimhin Kelly

Created: 11/02/2021
'''

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


def stack_averaging(Input_location,Output_location,stack):
    # This function reads in a stack and retrieves the average value of all bands

    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    # Mean Average is the default calculation no need to edit parameters
    #parameters.put('statistic', 'average')
    gcp = GPF.createProduct("Stack-Averaging",parameters,stack)

    output_path1 = os.path.join(Input_location,Output_location, 'Stack_Averaged_output4.dim')
    print("output_path", output_path1)
    ProductIO.writeProduct(gcp, output_path1, 'BEAM-DIMAP')

    print("A new .dim file has been outputted to", Output_location)

def create_stack(sen1_list):
    # This function reads a list of products and creates a single stack product

    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    # First product is declared as the Master
    parameters.put('extent','Master')
    sarlist = sen1_list
    # Please note the required function is Cross Correlation. NOT Create-Stack, as this leads to stack averaging issues
    stack = GPF.createProduct("Cross-Correlation", parameters, sarlist)

    return stack
    

def read_file(Input_location,Output_location,sen1_list):
    # The following loop walks through the folder and selects all .dim files.

    for ind,filePath in enumerate(glob.glob(os.path.join(Input_location, "*.dim"))):
       path, filename = os.path.split(filePath) 
       filename = os.path.splitext(filename)[0]

       inde = ind + 1
       Input = filePath
       print(inde,filename)
       # Try clause begins the processing steps
       try:
           product = ProductIO.readProduct(Input)
           sen1_list.append(product)
       except:
           print("File:", filename,"didnt work please check")

def main():
    
    # Declare Input and Output locations, An empty list is declared to hold Sentinel 1 data as a stack
    Input_location = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\Ireland\Sentinel-1\Repo\SNAP_test\output"
    Output_location = "stack"
    sen1_list = []

    # Read all files in folder and populate empty list
    read_file(Input_location,Output_location,sen1_list)
    
    print(sen1_list)

    # Create a single product holding all VV bands from original inputs
    stack = create_stack(sen1_list)
    
    # All bands in the stack are calculated into a single average product
    stack_averaging(Input_location,Output_location,stack)

if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")
