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
import psycopg2
from psycopg2 import Error

 
# https://github.com/senbox-org/snap-engine/blob/0fe1333118cb477666eb8d9231b9b0ae5a5559d8/snap-python/src/main/resources/snappy/examples/snappy_ndvi_with_masks.py#L33-L38
# https://github.com/senbox-org/snap-engine/blob/master/snap-python/src/main/resources/snappy/examples/snappy_geo_roi.py#L38   
    

def postgisdb_connect():
    
    connection = psycopg2.connect(user="postgres",
                                  password="HuufDorf13!",
                                  host="W19-PostGIS",
                                  port="5432",
                                  database="echoes_dev")

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")

    sql = "select guid, site_name, shape_type, country, ST_AsText(geom) as geom from internal_data.remote_sensing_sites where country = 'ireland' and site_name = 'Forest'"

    cursor.execute(sql)

    record = cursor.fetchall()
    #geom = record[0][0]
    myDict = dict() 
    
    myDict = record

    for i in myDict:
        print(i[4])
    #print(myDict)

def main():
    
    postgisdb_connect()

if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")
