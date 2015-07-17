for F in ../SRTM-filled/*
do
	echo $F
	name=$(basename $F)
	gdalwarp -of GTiff -co "TILED=YES" -co "COMPRESS=DEFLATE" -srcnodata 32767 \
	-t_srs "+init=epsg:3857 +over" \
	-r cubic -order 3 -multi composite/c_$name warped/w_$name
done

