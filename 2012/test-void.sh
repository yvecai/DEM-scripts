# compute max slope for a serie of DEM files
for X in ../SRTM-filled/*.tif
do
gdaldem roughness $X slopes.tif
rg=$(gdalinfo -stats slopes.tif | grep -o "Maximum=[0-9.]*" | grep -o "[0-9.]*")
echo $X $rg >> out.txt
done

