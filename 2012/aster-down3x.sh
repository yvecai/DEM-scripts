# ASTGTM2_N60E020_dem.tif.gz

for F in ASTER-data/*S56*.gz
do
rootname=${F:19:7}
echo $rootname
gzipname='/vsigzip/'$F
gdalwarp -ts 1201 1201 $gzipname ASTER-downsampledx3-tmp/$rootname.tif
done

for F in ASTER-data/*S57*.gz
do
rootname=${F:19:7}
echo $rootname
gzipname='/vsigzip/'$F
gdalwarp -ts 1201 1201 $gzipname ASTER-downsampledx3-tmp/$rootname.tif
done

for F in ASTER-data/*S58*.gz
do
rootname=${F:19:7}
echo $rootname
gzipname='/vsigzip/'$F
gdalwarp -ts 1201 1201 $gzipname ASTER-downsampledx3-tmp/$rootname.tif
done

for F in ASTER-data/*S59*.gz
do
rootname=${F:19:7}
echo $rootname
gzipname='/vsigzip/'$F
gdalwarp -ts 1201 1201 $gzipname ASTER-downsampledx3-tmp/$rootname.tif
done
