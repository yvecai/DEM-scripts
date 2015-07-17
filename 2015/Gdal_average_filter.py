#!/usr/bin/env python
# average x3 filter

# 13862

try:
    from osgeo import gdal
except ImportError:
    import gdal
from gdalconst import *

import sys
import os.path
import pdb
import struct
import numpy as np
import zipfile

def pt2fmt(pt):
    fmttypes = {
        GDT_Byte: 'B',
        GDT_Int16: 'h',
        GDT_UInt16: 'H',
        GDT_Int32: 'i',
        GDT_UInt32: 'I',
        GDT_Float32: 'f',
        GDT_Float64: 'f'
        }
    return fmttypes.get(pt, 'x')

NoDataValue=-32768


src_filename = sys.argv[1]
dst_filename = sys.argc[2]
print 'Processing ', src_filename
print 'to ', dst_filename

src_ds = gdal.Open( src_filename, gdal.GA_ReadOnly )

xsize = band.XSize  
ysize = band.YSize 

dst_ds = raster.Create(dst_filename, xsize, ysize, 2, gdal.GDT_Byte,
			options=[ 'TILED=YES', 'COMPRESS=DEFLATE', "BIGTIFF=YES", "ALPHA=YES" ])

projection   = src_ds.GetProjection()
geotransform = src_ds.GetGeoTransform()
dst_ds.SetGeoTransform(geotransform)
dst_ds.SetProjection(projection)

data=ds.GetRasterBand(2).ReadAsArray(0, 0, xsize, ysize)
z=numpy.zeros(data.shape, numpy.uint8)
dst_ds.GetRasterBand(1).WriteArray(z,0,0)

for x in range(1, xsize -1):
	for y in range(1, ysize -1):
		
		src_array = src_ds.GetRasterBand(2).ReadAsArray(x-1 , y-1 , 3, 3)
		mean=int(np.sum(src_array))+(src_array[1,1])/10
		dst_ds.GetRasterBand(2).WriteArray(np.array([[mean]]),x , y)


src_ds = None
aster_ds = None


