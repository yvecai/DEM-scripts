for F in ../SRTM-filled/*.tif
do
        echo $F
        name=$(basename $F)
        gdalwarp -of GTiff -co "TILED=YES" -srcnodata 32767 \
        -t_srs "+proj=merc +ellps=sphere +R=6378137 +a=6378137 +units=m" \
        -r bilinear -order 3 -multi $F warped
        #listgeo warped  > geo.txt
        ../src/gdal-1.9.1/apps/./gdaldem hillshade -z 0.5 -compute_edges warped hillshade.tif
        
        convert -level 28%x70% -negate hillshade.tif negate.tif
        
		SIZE=`identify -format "%wx%h" negate.tif`
		
		convert -size $SIZE xc:black black.png
		convert -depth 6 black.png negate.tif -alpha Off \
				-compose Copy_Opacity -composite alpha.png
		convert alpha.png slopes/hillshade_$name
        
        ./gdalcopyproj.py warped slopes/hillshade_$name
        
        rm warped hillshade.tif
        rm negate.tif
        rm alpha.png black.png

done
gdalbuildvrt big.vrt slopes/*.tif
