from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst

import sys
import os
import numpy
import pdb

import multiprocessing
import time
# ~ from multiprocessing import Process not ideal for clustering data in PG
# however the table being in need of cluster by st_geohash, why not ?
gdal.UseExceptions()
ogr.UseExceptions()
"""
After import sql:
# No need to keep space for future INSERT / UPDATE:
nohup psql -c 'ALTER TABLE contours SET (fillfactor = 100);' -d contours &
# Compress even smallgeometries (normally >2KB only), big reduction in disk space in conjonction with ST_QuantizeCoordinates():
nohup psql -c 'ALTER TABLE contours set (toast_tuple_target = 128);' -d contours &
# Cluster the data properly (big jump in access performance):
CREATE INDEX tmp_geohash ON contours (ST_GeoHash(ST_Transform(ST_Envelope(geom),4326))) WITH (fillfactor=100);
nohup psql -c 'CLUSTER VERBOSE contours USING tmp_geohash;' -d contours &

"""

database = 'contours_test'
usr = 'mapnik'
pw = 'mapnik'
table = 'contours'

error_file = open("errors.txt", "w")
err_count = 0

def work(infile,lon, lat, dlon, dlat,p):
	global err_count
	
	input_DEM=gdal.Open( infile, gdal.GA_ReadOnly ) # We have to open the file for each subprocess, gdal won't work properly with concurrent access.
	
	# Compute contours with a 2* pixel margin and shave it back to avoid artefact in block edges
	ulx = lon-2*src_res
	uly = lat+dlat+2*src_res
	lrx= lon+dlon+2*src_res
	lry= lat-2*src_res
	if ulx <= -180: ulx =-179.999
	if lrx >= 180: lrx=179.999
	if uly >= 90: uly=89.999
	if lry<=-90: lry=-89.999
	
	
	fulx = float(lon)
	fuly = float(lat+dlat)
	flrx= float(lon+dlon)
	flry= float(lat)
	if fulx <= -180: fulx =-179.999
	if flrx >= 180: flrx=179.999
	if fuly >= 90: fuly=89.999
	if flry <=-90: flry=-89.999
	
	proj_win=[ulx,uly,lrx,lry]
	final_win=[fulx,fuly,flrx,flry]
	
	srin = osr.SpatialReference()
	srin.ImportFromEPSG(4326)
	srin.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
	srout = osr.SpatialReference()
	srout.ImportFromEPSG(3857)
	
	transform = osr.CoordinateTransformation(srin,srout)
	
	# Create ring
	ring = ogr.Geometry(ogr.wkbLinearRing)
	ring.AddPoint(flrx,flry)
	ring.AddPoint(flrx,fuly)
	ring.AddPoint(fulx,fuly)
	ring.AddPoint(fulx,flry)
	ring.AddPoint(flrx,flry)

	# Create polygon
	bbox = ogr.Geometry(ogr.wkbPolygon)
	bbox.AddGeometry(ring)
	bbox.Transform(transform)
	
	# Work in memory to speed up process
	raster_drv= gdal.GetDriverByName("Memory")
	cropped_DEM = raster_drv.Create("/vsimem/cropped_DEM"+str(p), 0, 0, 0, gdal.GDT_Unknown)
	
	drv = ogr.GetDriverByName("ESRI Shapefile")
	tmp_Contour = drv.CreateDataSource("/vsimem/tmp_Contour"+str(p))
	
	ct_layer = tmp_Contour.CreateLayer("contours",geom_type=ogr.wkbLineString, srs=srin)
	field_defn = ogr.FieldDefn("C_ID", ogr.OFTInteger)
	ct_layer.CreateField(field_defn)
	field_defn = ogr.FieldDefn("ele", ogr.OFTInteger)
	ct_layer.CreateField(field_defn)
	connectionString = "PG:dbname='%s' user='%s' password='%s'" % (database,usr,pw)
	contourDB = ogr.Open(connectionString,1)
	
	# ~ final_layer = contourDB.CreateLayer(table,geom_type=ogr.wkbLineString, srs=srout, options=['GEOMETRY_NAME=geom'])
	for l in contourDB:
		if l.GetName() == table:
			final_layer = l
			
	print(proj_win, final_win)
	print("crop...")
	while True:
		try:
			gdal.Translate("/vsimem/cropped_DEM"+str(p), input_DEM, projWin=proj_win)
		except:
			#may be locked by another process
			print("Process "+str(p)+" waiting for input raster lock ...")
			time.sleep(5)
			continue
		break
	
	print("extracting contours...")
	
	ds=gdal.Open("/vsimem/cropped_DEM"+str(p), gdal.GA_ReadOnly)
	# Here it may be worth it to check if there is data in the cropped DEM to save some time over oceans
	gdal.ContourGenerate(ds.GetRasterBand(1), 10,0,[],0,0,ct_layer, 0,1)
	
	print("processing contours...")
	i = 0
	final_layer.StartTransaction()
	ogc_ids=''
	for feature in ct_layer:
		transformed = feature.GetGeometryRef()
		transformed.Transform(transform) # transform contour into epsg:3857
		
		geom = transformed.Simplify(4.0) # simplify contours with a 4m tolerance
		multi=geom.Intersection(bbox) # shave back the contour to the exact block extent
		defn = final_layer.GetLayerDefn()
		try:
			if multi.GetGeometryName() == 'LINESTRING':
				feat = ogr.Feature(defn)
				feat.SetField("ele", feature.GetField("ele"))
				feat.SetGeometry(multi)
				final_layer.CreateFeature(feat)
				ogc_ids += str(feat.GetFID()) + ','
				feat=None
			else: # After shaving the contours, they may be more complex geometries
				for m in multi:
				# multi could be linestring, multlinestring, or a collection including points, let's insert only linestrings
					if m.GetGeometryName() == 'LINESTRING':
						feat = ogr.Feature(defn)
						feat.SetField("ele", feature.GetField("ele"))
						feat.SetGeometry(m)
						final_layer.CreateFeature(feat)
						ogc_ids += str(feat.GetFID()) + ','
						feat=None
		except: # Now the script is working, maybe we can speed up the process ignoring logging errors
			error_file.write("ele: "+str(feature.GetField("ele"))+'\n')
			error_file.write(geom.ExportToWkt())
			error_file.write('\n')
			error_file.write(multi.ExportToWkt())
			error_file.write('\n')
			error_file.flush()
			err_count = err_count+1
			if err_count > 100: exit()
	
	
	ogc_ids=ogc_ids[:-1]
	final_layer.CommitTransaction()
	if len(ogc_ids)> 0: # there may be no features
		final_layer.StartTransaction()
		# Avoid storing unnecessary precision, toast better
		contourDB.ExecuteSQL("UPDATE %s set geom=ST_QuantizeCoordinates(ST_SnapToGrid(geom, 2),0) where ogc_fid in(%s) ;" %(table, ogc_ids))
		final_layer.CommitTransaction()
	
	raster_drv = None
	cropped_DEM = None
	ct_layer = None
	drv.DeleteDataSource("/vsimem/tmp_Contour"+str(p))
	drv = None
	tmp_Contour = None
	final_layer = None
	contourDB = None
	ds = None
	input_DEM = None
	
	print("done process", str(p),proj_win, final_win, flush=True)


nproc=4
# ~ gdal.SetConfigOption('GDAL_NUM_THREADS', '8') # speedup warping

infile=sys.argv[1]

src_res=0.0002777777777778966603
step = 0.25

processes=[]
p=0

# re-create layer if needed:
connectionString = "PG:dbname='%s' user='%s' password='%s'" % (database,usr,pw)
contourDB = ogr.Open(connectionString,1)
# ~ contourDB.ExecuteSQL("drop table %s;"%(table))

srout = osr.SpatialReference()
srout.ImportFromEPSG(3857)
final_layer = contourDB.CreateLayer(table, geom_type=ogr.wkbLineString,srs=srout, options=['GEOMETRY_NAME=geom'])
ele_field = ogr.FieldDefn("ele", ogr.OFTInteger)
final_layer.CreateField(ele_field)

# should be once at creation :
contourDB.ExecuteSQL("ALTER TABLE %s SET (autovacuum_enabled = off);"%(table))
contourDB.ExecuteSQL("ALTER TABLE %s SET (toast_tuple_target = 128);"%(table))

contourDB= None

for lat in numpy.arange(-70,72,step):
	for lon in numpy.arange(-180,180,step):
# ~ for lat in numpy.arange(45,46,step):
	# ~ for lon in numpy.arange(5,6,step):
		
		# poor man's process pool
		p += 1
		if p> 8:
			for p in processes:
				p.join()
			processes=[]
			p=0
			time.sleep(0.1)
		
		dlon=step
		dlat=step
		process= multiprocessing.Process(target=work, args=(infile,lon, lat, dlon, dlat,p))
		processes.append(process)
		process.start()
		print("process "+str(p)+" started")
		time.sleep(0.1)

