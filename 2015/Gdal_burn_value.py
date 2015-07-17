#!/usr/bin/env python
# Change no_data values and burn them in the file

# (c)Yves Cainaud, WTFPL

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
inNodata = int(sys.argv[2])
outNodata = int(sys.argv[3])
print "Replacing values ..."

src_ds = gdal.Open( src_filename, gdal.GA_Update )
band = src_ds.GetRasterBand(1)

xsize = band.XSize  
ysize = band.YSize 
BLOCKSIZE = 1024
xblocks = xsize/BLOCKSIZE
xrest = xsize - xblocks*BLOCKSIZE
yblocks = ysize/BLOCKSIZE
yrest = ysize - yblocks*BLOCKSIZE
#~ print xrest, yrest
#~ src_array = band.ReadAsArray(1,1,xsize-1,ysize-1)
#~ pdb.set_trace()
#~ src_array[src_array == inNodata] = outNodata
#~ band.WriteArray(src_array,1,1)

for i in range(0, xblocks):
	print xblocks, i
	for j in range(0, yblocks):
		#~ print i*BLOCKSIZE +1 , j*BLOCKSIZE +1, BLOCKSIZE, BLOCKSIZE
		src_array = band.ReadAsArray(i*BLOCKSIZE +1 , j*BLOCKSIZE +1 , BLOCKSIZE, BLOCKSIZE)
		src_array[src_array == inNodata] = outNodata
		
		if len(src_array[src_array == inNodata]): pdb.set_trace()
		band.WriteArray(src_array,i*BLOCKSIZE +1 , j*BLOCKSIZE +1)

for i in range(0, xblocks):
	#~ print i*BLOCKSIZE +1 , yblocks*BLOCKSIZE +1 , BLOCKSIZE, yrest, BLOCKSIZE, yrest
	src_array = src_ds.GetRasterBand(1).ReadAsArray(i*BLOCKSIZE +1 , yblocks*BLOCKSIZE +1 , BLOCKSIZE, yrest-1)
	src_array[src_array == inNodata] = outNodata
	if len(src_array[src_array == inNodata]): pdb.set_trace()
	band.WriteArray(src_array, i*BLOCKSIZE +1 , yblocks*BLOCKSIZE +1)

for j in range(0, yblocks):
	#~ print i*BLOCKSIZE +1 , xblocks*BLOCKSIZE +1 , BLOCKSIZE, xrest, xrest, BLOCKSIZE
	src_array = src_ds.GetRasterBand(1).ReadAsArray(xblocks*BLOCKSIZE +1 , j*BLOCKSIZE +1 , xrest-1, BLOCKSIZE)
	src_array[src_array == inNodata] = outNodata
	if len(src_array[src_array == inNodata]): pdb.set_trace()
	band.WriteArray(src_array, xblocks*BLOCKSIZE +1 , j*BLOCKSIZE +1)

#~ print xblocks*BLOCKSIZE +1 , yblocks*BLOCKSIZE +1 , xrest-1, yrest-1
src_array = src_ds.GetRasterBand(1).ReadAsArray(xblocks*BLOCKSIZE +1 , yblocks*BLOCKSIZE +1 , xrest-1, yrest-1)
src_array[src_array == inNodata] = outNodata
if len(src_array[src_array == inNodata]): pdb.set_trace()
band.WriteArray(src_array, xblocks*BLOCKSIZE +1 , yblocks*BLOCKSIZE +1)

#~ for x in range(1, xsize -1):
	#~ for y in range(1, ysize -1):
		#~ xmin = 
		#~ src_array = src_ds.GetRasterBand(2).ReadAsArray(x-1 , y-1 , 3, 3)
		#~ mean=int(np.sum(src_array))+(src_array[1,1])/10
		#~ dst_ds.GetRasterBand(2).WriteArray(np.array([[mean]]),x , y)
#~ 
#~ 
print "Done, refreshing stats ..."
band.ComputeStatistics(0)
band.SetNoDataValue(outNodata)
src_ds = None
#~ aster_ds = None


