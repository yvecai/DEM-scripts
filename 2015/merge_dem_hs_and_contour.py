#!/usr/bin/env python
# fill output with CGIAR, then ASTER, then SRTM, then EUDEM
# make hillshade
# make contour, take nodata into account

# Yves Cainaud, WTFPL, 08.2015

# 
CGIAR = True
ASTER = True
SRTM = True
EUDEM = True
HILLSHADE = True
CONTOURS = True

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
import scipy.signal
import zipfile
import subprocess

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

NoDataValue=-32767

test= False
i = 1

NODATA_LOG = open("nodata_log.txt",'w')

dsASTER=gdal.Open( "/home/website/ASTER_RAW/ASTER_RAW.tif", gdal.GA_ReadOnly )
#~ Origin = (-180.000138888888898,80.000138888888884)#~ Pixel Size = (0.000277777777778,-0.000277777777778)
if SRTM: dsSRTMGL1= gdal.Open( "/home/website/SRTMGL1/SRTM_RAW.tif", gdal.GA_ReadOnly )
#~ Origin = (-180.000138888888898,60.000138888888891)#~ Pixel Size = (0.000277777777778,-0.000277777777778)
dsEUDEM=gdal.Open( "/home/website/eudem/eudem-north.tif", gdal.GA_ReadOnly )
#~ Origin = (-34.999999999999993,75.000000000000000) #~ Pixel Size = (0.000277777777778,-0.000277777777778)
dsCGIAR = gdal.Open( "/home/website/CGIAR/SRTM_CGIAR_RAW_30m.tif", gdal.GA_ReadOnly )
# USE A ALREAD MADE FILE FOR RUNNING
#~ dest_ds=gdal.Open("zero-filled.tif", gdal.GA_Update )


# CREATE A NEW FILE
lon_o = -180
lat_o = 72
for lato in range(lat_o, -57, -1):
	for lono in range(lon_o, 180, 1):

#~ lon_o = 21
#~ lat_o = 43
#~ for lato in range(lat_o, 41, -1):
	#~ for lono in range(lon_o, 22, 1):
#~ lon_o = -27
#~ lat_o = 38
#~ for lato in range(lat_o, 37, -1):
	#~ for lono in range(lon_o, -25, 1):
#~ lon_o = 34 # Revda
#~ lat_o = 68 # Revda
#~ for lato in range(lat_o, lat_o-2, -1):
	#~ for lono in range(lon_o, lon_o+2, 1):
		if lono==-180: lono=-179.98 # gdalwarp issue
		ratio_dateline=1
		i=str(lato)+'-'+str(lono)
		print "\n"
		print "---------------------",i
		print "\n"
		res = 0.000277777777778
		BLOCK = int(1/res)+1
		EDGE = 50
		BLOCK+=2*EDGE
		
		xsize = BLOCK 
		ysize = BLOCK 
		
		# The Dateline trick
		if xsize*res+lono > 180:
			xsize=int((180-lono)/res)
			ratio_dateline =  float(xsize) / BLOCK
		
		print "create file ", xsize, ysize
		sys.stdout.flush()
		driver = gdal.GetDriverByName( "GTiff" )
		dest_ds=driver.Create("tmp/out_"+str(i)+".tif", xsize, ysize, 1, gdal.GDT_Float32,
					options=[ 'TILED=YES', "BIGTIFF=YES"])
		if SRTM: projection   = dsSRTMGL1.GetProjection()
		else: projection   = dsCGIAR.GetProjection()
		dest_ds.SetProjection( projection )
		#~ print lono -res/2 - res*(EDGE), res, 0.0, lato+res/2 + (EDGE)*res, 0.0, -res
		dest_ds.SetGeoTransform( [lono -res/2 - res*(EDGE), res, 0.0, lato+res/2 + (EDGE)*res, 0.0, -res] )
		
		print "zero-filling ..."
		sys.stdout.flush()
		dest_ds.GetRasterBand(1).Fill(-32767.)
		dest_ds.GetRasterBand(1).SetNoDataValue( -32767.)
		print "filled "
		sys.stdout.flush()
		
		dst_gt = gdal.InvGeoTransform(dest_ds.GetGeoTransform())
		gtASTER = gdal.InvGeoTransform(dsASTER.GetGeoTransform())
		if SRTM: gtSRTMGL1 = gdal.InvGeoTransform(dsSRTMGL1.GetGeoTransform())
		gtEUDEM = gdal.InvGeoTransform(dsEUDEM.GetGeoTransform())
		gtCGIAR = gdal.InvGeoTransform(dsCGIAR.GetGeoTransform())
		cols = dest_ds.RasterXSize
		rows = dest_ds.RasterYSize
		colsASTER = dsASTER.RasterXSize
		rowsASTER = dsASTER.RasterYSize
		if SRTM: colsSRTMGL1 = dsSRTMGL1.RasterXSize
		if SRTM: rowsSRTMGL1 = dsSRTMGL1.RasterYSize
		colsEUDEM = dsEUDEM.RasterXSize
		rowsEUDEM = dsEUDEM.RasterYSize
		colsCGIAR = dsCGIAR.RasterXSize
		rowsCGIAR = dsCGIAR.RasterYSize
		
		# --------------------------------------------------------------------------
		# copy CGIAR data
		# loop through the rows
		if CGIAR:
			cols_src = colsCGIAR
			rows_src = rowsCGIAR
			ds_src=dsCGIAR
			gt_src=gtCGIAR
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(dst_gt[1])[1],0,0)
			x_src,y_src = gdal.ApplyGeoTransform(gt_src[1], lon, lat)
			y_src = int(y_src)
			x_src = int(x_src)
			
			print x_src,y_src
			sys.stdout.flush()
			if y_src < 0:
				numRows_src = BLOCK + y_src
				y_src=0
			elif y_src + BLOCK < rows_src:
				numRows_src = BLOCK
			else:
				numRows_src = rows_src - y_src
				
			if x_src < 0:
				numCols_src = BLOCK + x_src
				x_src=0
			elif x_src + BLOCK < cols_src:
				numCols_src = BLOCK
			else:
				numCols_src = cols_src - x_src
			
			new_y_src = int(y_src)
			new_x_src = int(x_src)
			new_numRows_src = int(numRows_src)
			new_numCols_src = int(numCols_src)
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt_src[1])[1],new_x_src,new_y_src)
			
			path =""
			#~ 
			x_dest, y_dest = gdal.ApplyGeoTransform(dst_gt[1], lon, lat)
			x_dest = int(x_dest)
			y_dest = int(y_dest)
			
			# The dateline second trick
			if new_numCols_src> xsize : new_numCols_src= xsize # +180
			if x_dest+new_numCols_src>xsize: x_dest=xsize - new_numCols_src # -180
	
			# read the data in
			print "CGIAR: ",lon, lat #, loni, lati
			sys.stdout.flush()
			if not test and new_numCols_src>0 and new_numRows_src>0:
			#~ #	try:
					print new_x_src, new_y_src, new_numRows_src, new_numCols_src, x_dest , y_dest
					data = ds_src.GetRasterBand(1).ReadAsArray(new_x_src, new_y_src, new_numCols_src, new_numRows_src)
					data = data.astype(float)
					data[data == -32768.]= -32767.
					if -32767. in data: NODATA_LOG.write("CGIAR "+str(i)+"\n")
					#~ pdb.set_trace()
					#~ data[data == -32767.]= np.nan
					dest_ds.GetRasterBand(1).WriteArray(data, x_dest , y_dest)
			#~ #	except: 
			#~ #		print path
			dest_ds.FlushCache()
		# --------------------------------------------------------------------------
		# copy ASTER data
		# loop through the rows
		if ASTER:
			cols_src = colsASTER
			rows_src = rowsASTER
			ds_src=dsASTER
			gt_src=gtASTER
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(dst_gt[1])[1],0,0)
			x_src,y_src = gdal.ApplyGeoTransform(gt_src[1], lon, lat)
			y_src = int(y_src)
			x_src = int(x_src)
			
			print x_src,y_src
			sys.stdout.flush()
			if y_src < 0:
				y_src=0
			if x_src < 0:
				x_src=0
			if y_src + BLOCK < rows_src:
				numRows_src = BLOCK
			else:
				numRows_src = rows_src - y_src
			
			if x_src + BLOCK < cols_src:
				numCols_src = BLOCK
			else:
				numCols_src = cols_src - x_src
			
			new_y_src = int(y_src)
			new_x_src = int(x_src)
			new_numRows_src = int(numRows_src)
			new_numCols_src = int(numCols_src)
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt_src[1])[1],new_x_src,new_y_src)
			
			path =""
			#~ 
			x_dest, y_dest = gdal.ApplyGeoTransform(dst_gt[1], lon, lat)
			x_dest = int(x_dest)
			
			y_dest = int(y_dest)
			
			# The dateline second trick
			if new_numCols_src> xsize : new_numCols_src= xsize # +180
			if x_dest+new_numCols_src>xsize: x_dest=xsize - new_numCols_src # -180
			
			# read the data in
			print "ASTER: ",lon, lat #, loni, lati
			sys.stdout.flush()
			if not test and new_numCols_src>0 and new_numRows_src>0:
			#~ #	try:
					print new_x_src, new_y_src, new_numRows_src, new_numCols_src, x_dest , y_dest
					data = ds_src.GetRasterBand(1).ReadAsArray(new_x_src, new_y_src, new_numCols_src, new_numRows_src)
					data = data.astype(float)
					
					data[data == -32768.]= -32767.
					if -32767. in data: NODATA_LOG.write("ASTER "+str(i)+"\n")
					data[data == -32767.]= np.nan
					
					#mar=np.ma.masked_where(data == np.nan., data).mask
					
					kernel=np.ones((10,10),dtype=np.float)/100
					data = scipy.signal.convolve2d(data, kernel, mode='same')
					
					#data = data * (1-mar) -32767.*mar #refill nodata
					#~ data[data < -500]= -32767
					data[data == np.nan] = -32767.
					dest_ds.GetRasterBand(1).WriteArray(data, x_dest , y_dest)
			#~ #	except: 
			#~ #		print path
							
			dest_ds.FlushCache()
		# --------------------------------------------------------------------------		
		# copy SRTM data
		# loop through the rows
		if SRTM:
			cols_src = colsSRTMGL1
			rows_src = rowsSRTMGL1
			ds_src=dsSRTMGL1
			gt_src=gtSRTMGL1
			
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(dst_gt[1])[1],0,0)
			x_src,y_src = gdal.ApplyGeoTransform(gt_src[1], lon, lat)
			y_src = int(y_src)
			x_src = int(x_src)
			
			print x_src,y_src
			sys.stdout.flush()
			if y_src < 0:
				numRows_src = BLOCK + y_src
				y_src=0
			elif y_src + BLOCK < rows_src:
				numRows_src = BLOCK
			else:
				numRows_src = rows_src - y_src
				
			if x_src < 0:
				numCols_src = BLOCK + x_src
				x_src=0
			elif x_src + BLOCK < cols_src:
				numCols_src = BLOCK
			else:
				numCols_src = cols_src - x_src
			
			new_y_src = int(y_src)
			new_x_src = int(x_src)
			new_numRows_src = int(numRows_src)
			new_numCols_src = int(numCols_src)
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt_src[1])[1],new_x_src,new_y_src)
			
			path =""
			#~ 
			x_dest, y_dest = gdal.ApplyGeoTransform(dst_gt[1], lon, lat)
			x_dest = int(x_dest)
			y_dest = int(y_dest)
			
			# The dateline second trick
			if new_numCols_src> xsize : new_numCols_src= xsize # +180
			if x_dest+new_numCols_src>xsize: x_dest=xsize - new_numCols_src # -180
	
			# read the data in
			print "SRTM: ",lon, lat #, loni, lati
			sys.stdout.flush()
			if not test and new_numCols_src>0 and new_numRows_src>0:
			#~ #	try:
					print new_x_src, new_y_src, new_numRows_src, new_numCols_src, x_dest , y_dest
					data = ds_src.GetRasterBand(1).ReadAsArray(new_x_src, new_y_src, new_numCols_src, new_numRows_src)
					data = data.astype(float)
					kernel=np.ones((3,3),dtype=np.float)/9
					data[data == -32768.]= -32767.
					if -32767. in data: NODATA_LOG.write("SRTM "+str(i)+"\n")
					data[data == -32767.]= np.nan
					
					#~ # make a mask out of nodata, to keep data behind
					mar=np.ma.masked_where(data == np.nan , data).mask
					
					#~ pdb.set_trace()
					#~ # get the output values
					old = dest_ds.GetRasterBand(1).ReadAsArray(x_dest , y_dest, new_numCols_src, new_numRows_src)
					#~ # replace value where not nodata
					new = old * (mar) + data * (1 - mar)
					
					new = scipy.signal.convolve2d(new, kernel, mode='same')
					#~ new[new < -500]= -32767.
					new[new == np.nan] = -32767.
					dest_ds.GetRasterBand(1).WriteArray(new, x_dest , y_dest)
			#~ #	except: 
			#~ #		print path
			dest_ds.FlushCache()
		# --------------------------------------------------------------------------
		# copy EUDEM data
		# loop through the rows
		if EUDEM:
			cols_src = colsEUDEM
			rows_src = rowsEUDEM
			ds_src=dsEUDEM
			gt_src=gtEUDEM
			
			
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(dst_gt[1])[1],0,0)
			x_src,y_src = gdal.ApplyGeoTransform(gt_src[1], lon, lat)
			y_src = int(y_src)
			x_src = int(x_src)
			
			print x_src,y_src
			sys.stdout.flush()
			if y_src < 0:
				numRows_src = BLOCK + y_src
				y_src=0
			elif y_src + BLOCK < rows_src:
				numRows_src = BLOCK
			else:
				numRows_src = rows_src - y_src
				
			if x_src < 0:
				numCols_src = BLOCK + x_src
				x_src=0
			elif x_src + BLOCK < cols_src:
				numCols_src = BLOCK
			else:
				numCols_src = cols_src - x_src
			
			new_y_src = int(y_src)
			new_x_src = int(x_src)
			new_numRows_src = int(numRows_src)
			new_numCols_src = int(numCols_src)
			
			lon, lat = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt_src[1])[1],new_x_src,new_y_src)
			
			path =""
			#~ 
			x_dest, y_dest = gdal.ApplyGeoTransform(dst_gt[1], lon, lat)
			x_dest = int(x_dest)
			y_dest = int(y_dest)
			
			#~ loni, lati = gdal.ApplyGeoTransform(gdal.InvGeoTransform(dst_gt[1])[1], x_dest, y_dest)
			# read the data in
			print "EUDEM: ",lon, lat #, loni, lati
			sys.stdout.flush()
			if not test and new_numCols_src>0 and new_numRows_src>0:
				#~ try:
					print new_x_src, new_y_src, new_numRows_src, new_numCols_src, x_dest , y_dest
					data = ds_src.GetRasterBand(1).ReadAsArray(new_x_src, new_y_src, new_numCols_src, new_numRows_src)
					#~ data = data.astype(float)
					#~ # make a mask out of nodata, EUDEM is completed with zeros east of Europe
					mar=np.ma.masked_where(data <> 0. , data).mask
					
					if 0. in data: NODATA_LOG.write("EUDEM "+str(i)+"\n")
					
					#~ # get the output values
					old = dest_ds.GetRasterBand(1).ReadAsArray(x_dest , y_dest, new_numCols_src, new_numRows_src)
					#~ # replace value where not nodata
					new = old * (1-mar) + data * mar
					new[new == np.nan] = -32767.
					dest_ds.GetRasterBand(1).WriteArray(new, x_dest , y_dest)
				#~ except: 
					#~ print path
			dest_ds.FlushCache()
		
		
		if HILLSHADE :
			print "Creating Hillshading..."
			sys.stdout.flush()
			#dest_ds.GetRasterBand(1).GetStatistics(0,1)
			subprocess.call("gdaldem hillshade tmp/out_"+str(i)+".tif -z 2.0 -s 111170.0 -az 315.0 -alt 45.0 tmp/hillshade.tif", shell=True)
			print "Warping to 3857..."
			sys.stdout.flush()
			outWidth = int(3000 * ratio_dateline)
			subprocess.call("gdalwarp -of GTiff -co \"TILED=YES\" -co \"COMPRESS=DEFLATE\" -dstnodata 255 -t_srs \"+init=epsg:3857\" -r cubic -ts "+str(outWidth)+" 0 -multi -overwrite tmp/hillshade.tif tmp/3857_hillshade.tif", shell=True)
			print "Contrast Hillshading..."
			sys.stdout.flush()
			subprocess.call("gdaldem color-relief tmp/3857_hillshade.tif color_slope.txt tmp/contrast.tif", shell=True)
			
			print "Make output tile ..."
			sys.stdout.flush()
			toShave=gdal.Open( "tmp/contrast.tif", gdal.GA_ReadOnly )
			
			gt_warped = gdal.InvGeoTransform(toShave.GetGeoTransform())
			lono_out, lato_out = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt_warped[1])[1],0,0)
			#~ lono_out = gt_warped[1][0]
			#~ lato_out = gt_warped[1][3]
			reso = 1/gt_warped[1][1]
			
			cols = toShave.RasterXSize
			rows = toShave.RasterYSize
			projection   = toShave.GetProjection()
			
			ratioX=float(xsize)/cols
			ratioY=float(ysize)/rows
			EDGEX =int(EDGE/ratioX)-1
			EDGEY =int(EDGE/ratioY)-1
			
			dest_ds=driver.Create("out_hs/3857-out_"+str(i)+".tif", cols-2*EDGEX, rows-2*EDGEY, 2, gdal.GDT_Byte,
						options=[ 'TILED=YES', "BIGTIFF=YES", "COMPRESS=DEFLATE", "ALPHA=YES"])
			dest_ds.SetProjection( projection )
			
			dest_ds.SetGeoTransform( [lono_out +EDGEX*reso, reso, 0.0, lato_out-EDGEY*reso, 0.0, -reso] )
			dest_ds.GetRasterBand(1).Fill(0)
			
			data = toShave.GetRasterBand(1).ReadAsArray(EDGEX, EDGEY, cols-2*EDGEX, rows-2*EDGEY)
			#~ pdb.set_trace()
			dest_ds.GetRasterBand(2).WriteArray(data, 0, 0)
			dest_ds.GetRasterBand(1).GetStatistics(0,1)
			dest_ds.GetRasterBand(2).GetStatistics(0,1)
			print "DONE"
			sys.stdout.flush()
		if CONTOURS:
			
			print "Creating Contours..."
			sys.stdout.flush()
			toShave=gdal.Open( "tmp/out_"+str(i)+".tif", gdal.GA_ReadOnly )
			
			gt_warped = gdal.InvGeoTransform(toShave.GetGeoTransform())
			lono_out, lato_out = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt_warped[1])[1],0,0)
			#~ lono_out = gt_warped[1][0]
			#~ lato_out = gt_warped[1][3]
			reso = 1/gt_warped[1][1]
			
			cols = toShave.RasterXSize
			rows = toShave.RasterYSize
			projection   = toShave.GetProjection()
			
			ratioX=float(xsize)/cols
			ratioY=float(ysize)/rows
			EDGEX =int(EDGE/ratioX)-1
			EDGEY =int(EDGE/ratioY)-1
			
			# save the bare DEM
			dest_ds=driver.Create("out_dem/out_"+str(i)+".tif", cols-2*EDGEX, rows-2*EDGEY, 1, gdal.GDT_Float32,
						options=['TILED=YES',"BIGTIFF=YES", "COMPRESS=DEFLATE"])
			dest_ds.SetProjection( projection )
			
			dest_ds.SetGeoTransform( [lono_out +EDGEX*reso, reso, 0.0, lato_out-EDGEY*reso, 0.0, -reso] )
			data = toShave.GetRasterBand(1).ReadAsArray(EDGEX, EDGEY, cols-2*EDGEX, rows-2*EDGEY)
			#~ pdb.set_trace()
			dest_ds.GetRasterBand(1).WriteArray(data, 0, 0)
			
			dest_ds.GetRasterBand(1).SetNoDataValue( -32767. )
			dest_ds.FlushCache()
			#dest_ds.GetRasterBand(1).GetStatistics(0,1)
			subprocess.call("rm tmp/contours.* tmp/contours-3857.*", shell=True)
			subprocess.call("gdal_contour -i 10 -snodata -32767 -a height out_dem/out_"+str(i)+".tif tmp/contours.shp", shell=True)
			print "Exact cut to one degree and "
			print "projecting to EPSG 3857..."
			subprocess.call("ogr2ogr -f \"ESRI Shapefile\" -overwrite -clipsrc "+str(lono)+" "+str(lato-1)+" "+str(lono+1)+" "+str(lato)+" "+"-t_srs \"+init=epsg:3857\" tmp/contours-3857.shp tmp/contours.shp", shell=True)
			print "Simplifying ..."
			subprocess.call("ogr2ogr -f \"ESRI Shapefile\" -progress -overwrite -simplify 4 out_contours/contours_"+str(i)+".shp tmp/contours-3857.shp", shell=True)
			subprocess.call("gzip -f out_contours/*.shp", shell=True)
			subprocess.call("rm tmp/*", shell=True)
			
			
# gdalbuildvrt hillshade_05042015.vrt out/*
# nohup gdal_translate -stats -of GTiff -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=DEFLATE" -co "ALPHA=YES" hillshade_05042015.vrt hillshade_05042015.tif &


