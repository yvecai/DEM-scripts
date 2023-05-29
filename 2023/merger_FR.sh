# Small DEM to merge
A="../RGE_ALTI/RGE_Alti_5m.vrt"
# General DEM to merge into
B="../../dem2_4326_ZSTD_3.tif"
work_res=0.000277777777778
# 4 pix
cutline=0.001111111
# 3 pix
blend=0.000833333

# work on a small crop of the complete DEM plus a margin of 500m
python3 crop.py $A $B 500

# Warp the DEM to be merged to epsg:4326 and at the final resolution
gdalwarp -s_srs "epsg:2056" -t_srs "epsg:4326" -tr $work_res $work_res  -multi -wo NUM_THREADS=4 -overwrite -r cubicspline -dstnodata -32767 -overwrite -of GTiff -co "TILED=YES" -co "COMPRESS=DEFLATE" -co "NUM_THREADS=4" $A E_FR.tif
# compute isData(E) and extract a polygon shapefile
gdal_calc.py --calc="A != 9999" --overwrite --outfile Emask.tif -A E_FR.tif --co="TILED=YES" --co="COMPRESS=DEFLATE" --co="NUM_THREADS=4"
gdal_polygonize.py Emask.tif E_FR.shp
# compute cutline in QGis, draw big polygons over sea coasts and use 'dissolve' to simplify the borders, compute a 2x$work_res negative buffer 

# blend over 3px and overwrite
gdalwarp -s_srs "epsg:4326" -multi -wo NUM_THREADS=8 -cblend 3 -cutline E-Cutline-France.shp E_FR.tif C.tif

#~ burn back into big DEM
gdalwarp -multi -wo NUM_THREADS=8 C.tif $B


