for F in ../SRTM-filled/*.tif
do
	rm warped hillshade.tif 
	rm negate.tif 
	rm alpha.png black.png
	echo $F
	name=$(basename $F)
	gdalwarp -of GTiff -co "TILED=YES" -srcnodata 32767 \
	-t_srs "+proj=merc +ellps=sphere +R=6378137 +a=6378137 +units=m" \
	-r bilinear -order 3 -multi $F warped
	#listgeo warped  > geo.txt
	../src/gdal-1.9.1/apps/./gdaldem hillshade -z 2 -compute_edges warped hillshade.tif
	../src/gdal-1.9.1/apps/./gdaldem slope -compute_edges warped slopes.tif
	../src/gdal-1.9.1/apps/./gdaldem color-relief slopes.tif color_slope.txt slopes.tif
	composite hillshade.tif -compose Multiply slopes.tif hillshade.tif
	
	convert -level 28%x70% -negate hillshade.tif negate.tif
	
	SIZE=`identify -format "%wx%h" negate.tif`
	
	convert -size $SIZE xc:black black.png
	echo "black done"
	convert -depth 6 black.png negate.tif -alpha Off \
	-compose Copy_Opacity -composite alpha.png
	echo "Alpha done"
	convert alpha.png slopes/hillshade2_$name
	
	./gdalcopyproj.py warped slopes/hillshade2_$name
	
done
#sudo rm -r ../tiles/hillshading/1*
#./gdal2tiles_mod.py -z 0-11 -r cubicspline test/hillshade2_N46E006.tif ../tiles/hillshading

gdalbuildvrt big.vrt slopes/*.tif
