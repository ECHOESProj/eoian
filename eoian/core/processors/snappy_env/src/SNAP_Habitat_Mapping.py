"""
Name: Automated Snappy Habitat output

Description: The following script ingests a single Sentinel-2 tile. A number of Shapefiles are inputed and a Random Forest calculation is performed.
             Please note DIM files are produced to allow for processed data to be viewed when script is ran 
             
Minimum Requirements: Modules: Snappy, Numpy, os, sys,

Inputs: 1 zipped Sentinel-2 folder

Outputs: 1 GeoTIFF: 1 clipped site of the Wexford Slobs of modelled habitats, 3 .dim files of processed output data,

Author: Caoimhin Kelly,

Created: 20/01/2021,
"""

# Declare required Snappy modules
import os

import snappy
from snappy import GPF
from snappy import ProductIO
from snappy import WKTReader
from snappy import jpy


# This function creates a Random Forest classified dataset
def randomforestmodel(Output, resampled_product):
    # Shapefiles are defined
    Grass = r'D:\Projects\Active\Intereg_Echeos\RemoteSensing\Habitat_mapping\shps\Round2\Grass.shp'
    forest = r'D:\Projects\Active\Intereg_Echeos\RemoteSensing\Habitat_mapping\shps\Round2\Forest.shp'
    SandSoil = r'D:\Projects\Active\Intereg_Echeos\RemoteSensing\Habitat_mapping\shps\Round2\SandSoil.shp'
    Water = r'D:\Projects\Active\Intereg_Echeos\RemoteSensing\Habitat_mapping\shps\Round2\Water.shp'

    # Shapwfiles are loaded into the reampled product
    resampled_product_1 = loadVector(Grass, resampled_product)
    resampled_product_2 = loadVector(forest, resampled_product_1)
    resampled_product_3 = loadVector(SandSoil, resampled_product_2)
    resampled_product_4 = loadVector(Water, resampled_product_3)

    # Classifier product is created
    classifierParameters = snappy.HashMap()
    classifierParameters.put('trainOnRaster', False)

    # Reampled bands are added to the new Classifier product
    classifierParameters.put('featureBands', ','.join(
        [resampled_product_4.getBandAt(0).getName(), resampled_product_4.getBandAt(1).getName(),
         resampled_product_4.getBandAt(2).getName(), resampled_product_4.getBandAt(3).getName(),
         resampled_product_4.getBandAt(4).getName(), resampled_product_4.getBandAt(5).getName(),
         resampled_product_4.getBandAt(6).getName(), resampled_product_4.getBandAt(7).getName(),
         resampled_product_4.getBandAt(8).getName(), resampled_product_4.getBandAt(9).getName(),
         resampled_product_4.getBandAt(10).getName(), resampled_product_4.getBandAt(11).getName()]))
    classifierParameters.put('trainingVectors', 'Grass,Forest,SandSoil,Water')

    # To view the Classifier Parameters
    print("\n Model Inputs:", classifierParameters)

    # Random Forest model is performed
    classifierResult = GPF.createProduct('Random-Forest-Classifier', classifierParameters, resampled_product_4)

    # DIM file output is produced for Quality Control
    output_path = os.path.join(Output, 'snappy_rf_output3.dim')
    ProductIO.writeProduct(classifierResult, output_path, 'BEAM-DIMAP')
    # print("\n Random Forest DIM File have been written ..... ")

    print("\n Random Forest Modelling is complete...")

    return classifierResult


# Load Vector data into a product
def loadVector(file, product):
    # Creates a product which ingest a shapefile and adds to a product
    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('vectorFile', file)
    parameters.put('separateShapes', False)
    result = GPF.createProduct('Import-Vector', parameters, product)

    # Product is then returned
    return result


def VectorMasking(Output, modelled_product, StudyArea):
    StudyArea = loadVector(StudyArea, modelled_product)

    HashMap = jpy.get_type('java.util.HashMap')
    parameters = HashMap()
    parameters.put('geometry', 'Wexford_Slobs2')
    parameters.put('invertGeometry', False)
    parameters.put('useSRTM', False)
    parameters.put('byPass', False)
    result = GPF.createProduct('Land-Sea-Mask', parameters, StudyArea)

    GTiff_name = 'RF_Wexfordslobs.tif'
    # Declare where the image will be outputted
    path_collocated = os.path.join(Output, GTiff_name)

    # Write the image as a .GeoTIFF
    ProductIO.writeProduct(result, path_collocated, 'GeoTIFF')

    print("\n A Geotiff named", GTiff_name, "has been created")

    return result


# Resampling function
def resampling(Output, reproject_product):
    # All bands in a product need to be the same resolution, this function pairs all bands to a selected bands resolution
    parameters = snappy.HashMap()
    parameters.put('referenceBand', 'B2')

    operator_name = 'Resample'
    resampled_product = GPF.createProduct(operator_name, parameters, reproject_product)

    # If required a new DIM file can be written to output file for Quality Control
    output_path = os.path.join(Output, 'snappy_resampling_output2.dim')
    ProductIO.writeProduct(resampled_product, output_path, 'BEAM-DIMAP')

    print("\n Resampling is complete...")
    # Reampled Product is returned
    return resampled_product


# Reprojection function
def getReprojected(Output, subset_product):
    # For shapefiles to be added to a product projections must match
    ReprojectOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.reproject.ReprojectionOp')

    # Required Projection
    crs = 'EPSG:4326'

    # Build a new product containing the new projection
    op = ReprojectOp()
    op.setSourceProduct(subset_product)
    op.setParameter('crs', crs)
    op.setParameter('resampling', 'Nearest')

    reproject_product = op.getTargetProduct()

    print("\n Reprojection to ", crs, " is complete...")
    # A new product is returned in a new projection
    return reproject_product


# Subsetting function
def subset_dim(product):
    # This fuction subsets unnessary raw imagery
    SubsetOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')

    # Read the WKT of the site boundary as a geom
    wkt = "MultiPolygon (((-6.60903408269213966 52.28863356142135643, -6.60751865168285946 52.40219028680481017, -6.3424024156704073 52.40673657983264633, -6.3439178466796875 52.29317985444919259, -6.60903408269213966 52.28863356142135643)))"
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

    print("\n Subsetting is complete...")
    # A new subsetted product is returned
    return sub_product


# Processing function
def raw_processing(Input, Output, StudyArea):
    # This function pulls the methodology together
    # Call the zipped folder
    product = ProductIO.readProduct(Input)

    # Retrieves metadata
    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()
    name = product.getName()
    description = product.getDescription()
    band_names = product.getBandNames()

    # Printing of metadata
    print("\n Product:     %s, %s" % (name, description))
    print(" Raster size: %d x %d pixels" % (width, height))
    print(" Start time:  " + str(product.getStartTime()))
    print(" End time:    " + str(product.getEndTime()))
    print(" Bands:       %s" % (list(band_names)))

    # 1. Data is subsetted
    subset_product = subset_dim(product)

    # 2. Subsetted data is reprojected
    reproject_product = getReprojected(Output, subset_product)

    # 3. Reprojected data is resampled
    resampled_product = resampling(Output, reproject_product)

    # 4. Reprojected data is modelled using Random Forest function
    modelled_product = randomforestmodel(Output, resampled_product)

    # 5 Modelled classification is masked with site boundary
    output = VectorMasking(Output, modelled_product, StudyArea)


def main():
    Input = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\Ireland\Sentinel-2\Repo\S2B_MSIL2A_20201106T114349_N0214_R123_T29UPU_20201106T132455.zip"

    StudyArea = r'D:\Projects\Active\Intereg_Echeos\RemoteSensing\Habitat_mapping\shps\Round2\Wexford_Slobs2.shp'

    Output = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\snappy"

    raw_processing(Input, Output, StudyArea)


if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print("Done!")
