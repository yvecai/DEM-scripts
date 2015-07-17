#!/usr/bin/env python
# fill SRTM voids from ASTER data
# Override input SRTM file 
# Gzipped Aster directory and filename hardcoded

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
aster_dir='ASTER-data/'
base_name=src_filename.split('/')[1].split('.')[0]
aster_filename='/vsigzip/'+aster_dir+'ASTGTM2_'+base_name+'_dem.tif.gz'
print 'Processing ', src_filename
print 'with ', aster_filename

src_band = 1
src_ds = gdal.Open( src_filename, gdal.GA_Update )

cols = src_ds.RasterXSize
rows = src_ds.RasterYSize
src_band = src_ds.GetRasterBand(src_band)

aster_band = 1
aster_ds = gdal.Open( aster_filename, gdal.GA_ReadOnly )
aster_band = aster_ds.GetRasterBand(aster_band)

factor=3601./1201.
listnodata=[]
n=0
for x in range(cols) :
	for y in range(rows):
		pixel = src_band.ReadRaster(x , y , 1, 1, 1, 1)
		fmt = pt2fmt(src_band.DataType)
		pixval = struct.unpack(fmt, pixel)[0]
		if pixval < 0:
			n+=1
			listnodata.append((x,y))
			try: 
				asterpixel = aster_band.ReadAsArray(int(factor*x) , int(factor*y) , 3, 3)
				mean=np.sum(asterpixel)/9
				src_band.WriteArray(np.array([[mean]]), x,y)
			except: pass
			

# smoothing: average filter 3x3
for (x,y) in listnodata:
	try:
		src_array = src_band.ReadAsArray(x-1 , y-1 , 3, 3)
		mean=int(np.sum(src_array))/9
		src_band.WriteArray(np.array([[mean]]),x , y)
	except: pass
	

src_ds = None
aster_ds = None

print 'Number of void filled: ',n

