"Name: Automated Snappy NDWI output"

"Description: The following script ingests a single Sentinel-2 tile and processes the NDWI calculation. It then segments the high water values"

"Minimum Requirements: Modules: Snappy, Numpy, os, sys",

"Inputs: 1 zipped Sentinel-2 folder"

"Outputs: 2 GeoTIFFS: 1 of a clipped site of the Wexford Slobs, 1 of the segmented water area.",

"Author: Caoimhin Kelly",

"Created: 08/01/2021",

#  Copyright (c) 2022.
#  The ECHOES Project (https://echoesproj.eu/) / Compass Informatics

import matplotlib.pyplot as plt
import numpy
# Declare required Snappy modules
import os
import snappy
import sys
# import configparser
# import Automation.utils.handler as handler
from pathlib import Path
from snappy import FlagCoding
from snappy import Product
from snappy import ProductData
from snappy import ProductIO
from snappy import ProductUtils
from snappy import WKTReader
from snappy import jpy, GPF


# CONFIG_PATH=str(Path(__file__).parent / "config.ini").replace("GIS_processing","Automation")
# with open(CONFIG_PATH, 'r') as f:
#     config_string = f.read()
#
# config = configparser.ConfigParser()
# config.read_string(config_string)
#
# output_path=config.get("SNAP", "Output")
# input_path=config.get("Sentinel", "Downloads")

# logger = handler.initialize()

def segmentation_process(Output, sub_product):
    try:
        # HashMap store items in "key/value" pairs
        params = snappy.HashMap()
        # Return the Band Math object
        BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
        targetBand = BandDescriptor()
        targetBand.name = 'ndwi'
        targetBand.type = 'float32'
        # Insert the calculation for extracted pixel values
        targetBand.expression = 'if ndwi <= 0.376 AND ndwi >=0.07 theN 1 else 0'
        # Create an array of the pixels from the calcuations
        targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
        targetBands[0] = targetBand
        # Store these new pixels as a pair
        params.put('targetBands', targetBands)
        # Create the new product of the segmented pixels
        product3 = GPF.createProduct('BandMaths', params, sub_product)
        # Create the path for the export of the new image
        path_collocated = os.path.join(Output, 'NDWI_sgement.tif')
        # Write the new dataset as a GeoTIFF
        ProductIO.writeProduct(product3, path_collocated, 'GeoTIFF')
    except Exception as e:
        logger.error(e);


def subset_dim(input_path, output_path):
    try:
        product2 = ProductIO.readProduct(input_path)

        # product2 = ProductIO.readProduct(ndviProduct)

        # Return a type object for the given, fully qualified Java type name which is the name of a Java primitive type, a Java class name, or a Java array type name.
        SubsetOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')

        # Read the WKT of the site boundary as a geom
        wkt = "POLYGON((-6.37782096862793 52.3523807018953,-6.37722015380859 52.3530622304732,-6.37670516967773 52.3536913244486,-6.37619018554687 52.3541631390539,-6.37558937072754 52.3548970628732,-6.37490272521973 52.3557358180288,-6.3746452331543 52.3562076108085,-6.37413024902344 52.3590906794698,-6.3749885559082 52.3608728460197,-6.37576103210449 52.3620783885164,-6.37627601623535 52.3624976999357,-6.37696266174316 52.3633363108363,-6.37722015380859 52.3639652585661,-6.37722015380859 52.3647514306377,-6.37696266174316 52.3652755375801,-6.37696266174316 52.3663237328124,-6.37679100036621 52.3670050463769,-6.37687683105469 52.3675815342629,-6.37953758239746 52.3698874105766,-6.38228416442871 52.3711975139489,-6.38254165649414 52.3721931665239,-6.38339996337891 52.3730839945403,-6.38365745544434 52.3743940031011,-6.38520240783691 52.3750751921967,-6.38614654541016 52.3755991766591,-6.38700485229492 52.374760798535,-6.38794898986816 52.3739748045892,-6.38889312744141 52.3732935985212,-6.39026641845703 52.3724551766292,-6.3914680480957 52.3718263497654,-6.39241218566895 52.3717739471226,-6.39352798461914 52.3720359597148,-6.39464378356934 52.3725075784637,-6.39515876770019 52.3731887966551,-6.39610290527344 52.3740272046208,-6.39824867248535 52.3745512015172,-6.40030860900879 52.3744464026353,-6.40168190002441 52.3740272046208,-6.40202522277832 52.3736604030942,-6.40374183654785 52.373345999361,-6.405029296875 52.3730315933896,-6.40631675720215 52.3732935985212,-6.4076042175293 52.3733984001386,-6.40872001647949 52.373345999361,-6.40983581542969 52.3731363956288,-6.41095161437988 52.3728219881653,-6.41206741333008 52.3721407643164,-6.41292572021484 52.3713547237424,-6.4134407043457 52.3707782850975,-6.41352653503418 52.370044625033,-6.41412734985352 52.3696253852392,-6.41481399536133 52.3693109527826,-6.41558647155762 52.3689965180878,-6.41773223876953 52.3689965180878,-6.41970634460449 52.3687868937145,-6.42082214355469 52.3685772683463,-6.42228126525879 52.3682104215585,-6.42374038696289 52.3674767188432,-6.42374038696289 52.3664285509678,-6.4240837097168 52.3655375887197,-6.42434120178223 52.3644369634878,-6.42511367797852 52.3633363108363,-6.42545700073242 52.3623928724539,-6.42640113830566 52.3609252615948,-6.42897605895996 52.3578326362757,-6.43077850341797 52.3561027684039,-6.42374038696289 52.3562076108085,-6.41979217529297 52.3560503471083,-6.41867637634277 52.3560896630858,-6.41470670700073 52.3557489234518,-6.41234636306763 52.3555916581193,-6.40869855880737 52.3555916581193,-6.40846252441406 52.3556571854092,-6.40689611434936 52.355683396298,-6.40217542648315 52.3552902313344,-6.40168190002441 52.3552902313344,-6.40148878097534 52.3554606032481,-6.39867782592773 52.355368864607,-6.39462232589722 52.3557751342862,-6.38964414596558 52.3556571854092,-6.38934373855591 52.3555654471762,-6.38895750045776 52.3556571854092,-6.38593196868896 52.3554737087527,-6.38442993164062 52.3551853867534,-6.38327121734619 52.3547922173595,-6.38144731521606 52.3541500331607,-6.37988090515137 52.3535733700103,-6.37837886810303 52.3527869990433,-6.37782096862793 52.3523807018953))"
        geom = WKTReader().read(wkt)

        op = SubsetOp()
        # Set the Source Product
        op.setSourceProduct(product2)
        # Set the Subset Region
        op.setGeoRegion(geom)
        # Copy the Metadata from the raw data
        op.setCopyMetadata(True)
        # Subset the site from the image
        sub_product = op.getTargetProduct()

        # Declare where the image will be outputted
        path_collocated = os.path.join(Output, 'NDWI_output.tif')

        # Write the image as a .GeoTIFF
        ProductIO.writeProduct(sub_product, output_path, 'GeoTIFF')

        return sub_product
    except Exception as e:
        logger.error(e);


# Processing function
def raw_processing(Input, Output, dimfile):
    try:
        # Call the zipped folder
        product = ProductIO.readProduct(Input)

        # print(list(product.getBandNames()))

        # Retrieves metadata
        width = product.getSceneRasterWidth()
        height = product.getSceneRasterHeight()
        name = product.getName()
        description = product.getDescription()
        band_names = product.getBandNames()

        # Printing of metadata
        print("Product:     %s, %s" % (name, description))
        print("Raster size: %d x %d pixels" % (width, height))
        print("Start time:  " + str(product.getStartTime()))
        print("End time:    " + str(product.getEndTime()))
        print("Bands:       %s" % (list(band_names)))

        # Select bands from data, note B3 + B8 are needed for calculating NDWI
        B3 = product.getBand('B3')
        B8 = product.getBand('B8')

        # Create a new NDWI product and add a new band for NDWI
        ndwiProduct = Product('NDWI', 'NDWI', width, height)
        ndwiBand = ndwiProduct.addBand('ndwi', ProductData.TYPE_FLOAT32)
        # Create a .dim product to export the new product
        writer = ProductIO.getProductWriter('BEAM-DIMAP')
        # Copy the metadata from the oringal dataset
        ProductUtils.copyGeoCoding(product, ndwiProduct)

        # Write the new product to file
        output_path = os.path.join(Output, dimfile)

        ndwiProduct.setProductWriter(writer)
        ndwiProduct.writeHeader(output_path)

        # Create 2 new areas for calculating the NDWI bands
        b3 = numpy.zeros(width, dtype=numpy.float32)
        b8 = numpy.zeros(width, dtype=numpy.float32)

        # Loop through all pixels and calculate the NDWI for that pixel
        for y in range(height):
            b3 = B3.readPixels(0, y, width, 1, b3)
            b8 = B8.readPixels(0, y, width, 1, b8)
            # Excute the following formula for NDWI
            ndwi = (b3 - b8) / (b3 + b8)
            ndwiBand.writePixels(0, y, width, 1, ndwi)
        # Close the product
        ndwiProduct.closeIO()

        # Calling the subset function the processed NDWI product can be subsetted from a full tile to the bounds of the WKT entry
        sub_product = subset_dim(dimfile, )

        # Specific pixel values can be extracted from the image using a select Query
        segmentation_process(Output, sub_product)
    except Exception as e:
        logger.error(e);


def main(input_file, output_path):

    raw_processing(input_file, output_path, dimfile)

    print("ran")


if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    Input = r"C:\Users\ckelly.COMPASSINFORMAT\Echoes\Ireland\Sentinel-2\Repo\S2B_MSIL2A_20201106T114349_N0214_R123_T29UPU_20201106T132455.zip"
    main(Input, r"C:\data\temp\snappy_ndwi_output.dim")
    print("Done!")
