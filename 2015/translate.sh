#~ cd DATA
#~ for x in *.zip
#~ do
#~ unzip $x
#~ rm $x
#~ done
#~ cd ..
gdalbuildvrt SRTM_RAW_03-2015.vrt DATA/*.hgt

gdal_translate -of GTiff -a_nodata -32767 -co "BIGTIFF=YES" -co "COMPRESS=DEFLATE" -co "TILED=YES"\
	SRTM_RAW_03-2015.vrt SRTM_RAW_03-2015.tif
	
#~ ./Gdal_burn_value.py SRTM_RAW_03-2015.tif -32767 -32767

