for F in ../SRTM-filled/*.tif
do
	rm slopes.tif
	echo $F
	name=$(basename $F)

	#listgeo warped  > geo.txt
	gdaldem hillshade -z 2 -s 111120 -compute_edges $F hillshade/hs_$name
	gdaldem slope -compute_edges -s 111120 $F slopes.tif
	gdaldem color-relief slopes.tif color_slope.txt slopes/s_$name	
	
done

