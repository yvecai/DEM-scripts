#gdalbuildvrt data-SRTM-filled.vrt ../SRTM-filled/*.tif
gdaldem hillshade -z 2 -s 111120 data-SRTM-filled.vrt wgs84-hillshade.tif
#gdalwarp -of GTiff -co "BIGTIFF=YES" -co "compress=deflate" -srcnodata 32767 \
#	-t_srs "+proj=merc +ellps=sphere +R=6378137 +a=6378137 +units=m" \
#	-r cubic -order 3 -multi data-SRTM-filled.vrt warped-data-SRTM-filled.tif

