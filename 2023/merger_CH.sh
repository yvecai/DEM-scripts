
#~ gdal_translate  --config GDAL_CACHEMAX 1000 --config GDAL_DISABLE_READDIR_ON_OPEN TRUE -co "BIGTIFF=YES" -co "TILED=YES" -co "BLOCKXSIZE=3200" -co "BLOCKYSIZE=3200" -co "COMPRESS=ZSTD" -co "ZSTD_LEVEL=3" -co "NUM_THREADS=8" dem2.vrt dem2_4326.tif
#327GB

# Small DEM to merge
A="../Swiss_Alti3D/Swiss_alti3D_2m.vrt"
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
gdalwarp -s_srs "epsg:2056" -t_srs "epsg:4326" -tr $work_res $work_res  -multi -wo NUM_THREADS=4 -overwrite -r cubicspline -dstnodata -32767 -overwrite -of GTiff -co "TILED=YES" -co "COMPRESS=DEFLATE" -co "NUM_THREADS=4" $A E_CH.tif

# compute isData(E) and extract a polygon shapefile
gdal_calc.py --calc="A != 9999" --overwrite --outfile Emask.tif -A E_CH.tif --co="TILED=YES" --co="COMPRESS=DEFLATE" --co="NUM_THREADS=4"
gdal_polygonize.py Emask.tif E_CH.shp
# compute cutline
ogr2ogr E_CH-valid.shp E_CH.shp -a_srs "epsg:4326" -makevalid -overwrite
# rest may fail because of null entities in the shapefile ?!
ogr2ogr E_CH-cutline.shp E_CH-valid.shp -makevalid -a_srs "epsg:4326" -dialect sqlite -sql "select Buffer(geometry,-0.001111111,2) as geometry from 'E-valid'" -overwrite

# blend over 3px and overwrite
gdalwarp -s_srs "epsg:4326" -multi -wo NUM_THREADS=8 -cblend 3 -cutline E-cutline.shp E_CH.tif C.tif

#~ burn back into big DEM
gdalwarp -multi -wo NUM_THREADS=8 C.tif $B


