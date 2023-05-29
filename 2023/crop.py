from osgeo import gdal, osr
# ~ from gdalconst import *

import sys
import os.path
import pdb

print("crop.py A B margin - crops Bto A extent + margin in source srs\n")
# ~ pdb.set_trace()
A=gdal.Open(sys.argv[1])

ulx, xres, xskew, uly, yskew, yres  = A.GetGeoTransform()
lrx = ulx + (A.RasterXSize * xres)
lry = uly + (A.RasterYSize * yres)
print(ulx, uly, lrx, lry)

proj = osr.SpatialReference(wkt=A.GetProjection())
epsgCode=proj.GetAttrValue('AUTHORITY',1)

B=gdal.Open(sys.argv[2])
margin=float(sys.argv[3])
outExtent=[ulx + margin, uly + margin, lrx - margin, lry - margin]
print(outExtent)
gdal.Translate("C.tif", B, projWin=outExtent,projWinSRS="epsg:"+epsgCode,
								format="GTiff",
								creationOptions=["TILED=YES","COMPRESS=DEFLATE","NUM_THREADS=4","BIGTIFF=YES","COMPRESS=ZSTD","ZSTD_LEVEL=2"])
