for F in ../SRTM-filled/*.tif
do
	rm composed.tif
	echo $F
	name=$(basename $F)

	#listgeo warped  > geo.txt
	composite -compose Multiply hillshade/hs_$name slopes/s_$name composed.tif
	convert -level 28%x70% composed.tif composite/c_$name
	./gdalcopyproj.py hillshade/hs_$name composite/c_$name
done

