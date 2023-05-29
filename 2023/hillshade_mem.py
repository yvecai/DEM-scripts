from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array

from osgeo import gdalconst
import sys
import os
import pdb

## Crop a global epsg:4326 DEM in 10° squares, compute hillshading and 
## wrap output to epsg:3857. No edge effects
## takes ~9h on 8 cores, nvme disk for a 1 arcsec / 30m DEM

gdal.SetConfigOption('GDAL_NUM_THREADS', '8') # speedup warping

infile=sys.argv[1]
input_DEM=gdal.Open( infile, gdal.GA_ReadOnly )
src_res=0.0002777777777778966603
# ~ for lat in range(80,90,10):
	# ~ for lon in range(-180,180,10):
# ~ for lat in range(-70,70,10):
	# ~ for lon in range(-180,180,10):
		
		# ~ ulx = lon-2*src_res
		# ~ uly = lat+10+2*src_res
		# ~ lrx= lon+10+2*src_res
		# ~ lry= lat-2*src_res
		# ~ if ulx <= -180: ulx =-179.999
		# ~ if lrx >= 180: lrx=179.999
		# ~ if uly >= 90: uly=89.999
		# ~ if lry<=-90: lry=-89.999
		
		
		# ~ fulx = lon
		# ~ fuly = lat+10
		# ~ flrx= lon+10
		# ~ flry= lat
		# ~ if fulx <= -180: fulx =-179.999
		# ~ if flrx >= 180: flrx=179.999
		# ~ if fuly >= 90: fuly=89.999
		# ~ if flry <=-90: flry=-89.999
		
		# ~ proj_win=[ulx,uly,lrx,lry]
		# ~ final_win=[fulx,fuly,flrx,flry]
		
		# ~ cropped_DEM = gdal.GetDriverByName("Memory").Create("cropped_DEM", 0, 0, 0, gdal.GDT_Unknown)
		# ~ tmp_Hillshade = gdal.GetDriverByName("Memory").Create("tmp_Hillshade", 0, 0, 0, gdal.GDT_Unknown)
		# ~ tmp_Hillshade_3857 = gdal.GetDriverByName("Memory").Create("tmp_Hillshade_3857", 0, 0, 0, gdal.GDT_Unknown)
		# ~ final_Hillshade="../hillshade_tiles/mem_HS_tile_3857_"+str(lon)+"_"+str(lat)+".tif"
		
		# ~ print(proj_win, final_win)
		# ~ print("crop...")
		# ~ gdal.Translate("/vsimem/cropped_DEM", input_DEM, projWin=proj_win)
		
		# ~ print("hillshading...")
		# ~ gdal.DEMProcessing("/vsimem/tmp_Hillshade",
					# ~ "/vsimem/cropped_DEM",
					# ~ "hillshade",
					# ~ zFactor= 2,
					# ~ scale=111120,
					# ~ azimuth= 320.0,
					# ~ igor=True)
		# ~ print("warping...")
		# ~ gdal.Warp("/vsimem/tmp_Hillshade_3857",
						# ~ "/vsimem/tmp_Hillshade",
						# ~ srcSRS="epsg:4326",
						# ~ dstSRS="epsg:3857",
						# ~ xRes=30,
						# ~ yRes=30,
						# ~ resampleAlg="cubic")
		# ~ print("shaving...")
		# ~ gdal.Translate(final_Hillshade,"/vsimem/tmp_Hillshade_3857",
						# ~ projWin=final_win,
						# ~ projWinSRS="epsg:4326",
						# ~ format="GTiff",
						# ~ creationOptions=["TILED=YES","NUM_THREADS=4","BIGTIFF=YES","COMPRESS=DEFLATE"])
						# creationOptions=["TILED=YES","NUM_THREADS=4","BIGTIFF=YES","COMPRESS=ZSTD","ZSTD_LEVEL=2"]) ZSTD may cause incompativbility with mapnik
		
		# ~ try:
			# ~ os.remove(cropped_DEM)
			# ~ os.remove(tmp_Hillshade)
			# ~ os.remove(tmp_Hillshade_3857)
		# ~ except: pass
		# ~ print("done.\n")

for lat in range(70,72,2):
	for lon in range(-180,180,10):
		
		ulx = lon-2*src_res
		uly = lat+2+2*src_res
		lrx= lon+10+2*src_res
		lry= lat-2*src_res
		if ulx <= -180: ulx =-179.999
		if lrx >= 180: lrx=179.999
		if uly >= 90: uly=89.999
		if lry<=-90: lry=-89.999
		
		
		fulx = lon
		fuly = lat+2
		flrx= lon+10
		flry= lat
		if fulx <= -180: fulx =-179.999
		if flrx >= 180: flrx=179.999
		if fuly >= 90: fuly=89.999
		if flry <=-90: flry=-89.999
		
		proj_win=[ulx,uly,lrx,lry]
		final_win=[fulx,fuly,flrx,flry]
		
		cropped_DEM = gdal.GetDriverByName("Memory").Create("cropped_DEM", 0, 0, 0, gdal.GDT_Unknown)
		tmp_Hillshade = gdal.GetDriverByName("Memory").Create("tmp_Hillshade", 0, 0, 0, gdal.GDT_Unknown)
		tmp_Hillshade_3857 = gdal.GetDriverByName("Memory").Create("tmp_Hillshade_3857", 0, 0, 0, gdal.GDT_Unknown)
		final_Hillshade="../hillshade_tiles/mem_HS_tile_3857_"+str(lon)+"_"+str(lat)+".tif"
		
		print(proj_win, final_win)
		print("crop...")
		gdal.Translate("/vsimem/cropped_DEM", input_DEM, projWin=proj_win)
		
		print("hillshading...")
		gdal.DEMProcessing("/vsimem/tmp_Hillshade",
					"/vsimem/cropped_DEM",
					"hillshade",
					zFactor= 2,
					scale=111120,
					azimuth= 320.0,
					igor=True)
		print("warping...")
		gdal.Warp("/vsimem/tmp_Hillshade_3857",
						"/vsimem/tmp_Hillshade",
						srcSRS="epsg:4326",
						dstSRS="epsg:3857",
						xRes=30,
						yRes=30,
						resampleAlg="cubic")
		print("shaving...")
		gdal.Translate(final_Hillshade,"/vsimem/tmp_Hillshade_3857",
						projWin=final_win,
						projWinSRS="epsg:4326",
						format="GTiff",
						creationOptions=["TILED=YES","NUM_THREADS=4","BIGTIFF=YES","COMPRESS=DEFLATE"])
						# ~ creationOptions=["TILED=YES","NUM_THREADS=4","BIGTIFF=YES","COMPRESS=ZSTD","ZSTD_LEVEL=2"]) ZSTD may cause incompativbility with mapnik
		
		try:
			os.remove(cropped_DEM)
			os.remove(tmp_Hillshade)
			os.remove(tmp_Hillshade_3857)
		except: pass
		print("done.\n")
# ~ gdal_translate  --config GDAL_CACHEMAX 1000 --config GDAL_DISABLE_READDIR_ON_OPEN TRUE -co "BIGTIFF=YES" -co "TILED=YES" -co "COMPRESS=DEFLATE" -co "NUM_THREADS=8" ../hillshade.vrt ../Hillshade3.tif
# ~ gdaladdo -ro --config COMPRESS_OVERVIEW DEFLATE --config GDAL_NUM_THREADS 8 --config GDAL_CACHEMAX 1000 Hillshade3.tif 2 4 8 16 32
