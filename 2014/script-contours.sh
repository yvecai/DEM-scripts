#!/bin/bash
LOG="import-contours.log"
PREP_TABLE="1"
for X in tiles/*.tif; do
	
	# Import 10m contours
	gdal_contour -i 10 -snodata -32768 -a height $X contours.shp
	ogr2ogr -append -t_srs EPSG:3857 -f "PostgreSQL" 'PG:dbname='contours'' -lco DIM=2 contours.shp
	# [ "$PREP_TABLE" ] && /usr/lib/postgresql/9.1/bin/shp2pgsql -p -I -g way shape.shp contours | psql -U mapnik -q contours
	# /usr/lib/postgresql/9.1/bin/shp2pgsql -a -g way shape.shp contours | psql -U mapnik -q contours
	rm -f *.shp *.shx *.dbf
	rm -f *.prj
	# unset PREP_TABLE
    echo $(date)' '$X' done'>> $LOG
done
echo 'DONE'>> $LOG


exit 0
#~ 
createdb -U mapnik contours
psql -d contours -U mapnik  -f /usr/share/postgresql/9.3/contrib/postgis-2.1/postgis.sql
psql -d contours -U mapnik -f /usr/share/postgresql/9.3/contrib/postgis-2.1/spatial_ref_sys.sql


#~ #echo "ALTER USER mapnik WITH PASSWORD 'mapnik';"  | psql -d contour # not usefull
#~ exit
#~ dropdb contours
#~ 
#~ # test:
#~ 457 GB
#~ select count(*) from contours where ST_intersects(way, ST_MakeEnvelope(-180,72,180,85));
#~ echo "select count(*) from contours where ST_intersects(way, ST_MakeEnvelope(-180,72,180,85));" | psql -d contours
#~ 
#~ 963GB
#~ echo "vacuum;" | psql -d contours
#~ # size of the db:
#~ cd /var/lib/postgresql/8.4/main/base
#~ du -sh *
#~ 
#~ shared_buffers = 256MB
#~ time shp2pgsql -a -g way N06E124 contours | psql -U mapnik -q contour
#~ real	6m45.981s
#~ user	1m0.400s
#~ sys	0m15.977s
#~ 
#~ shared_buffers = 4100MB
#~ sudo /etc/init.d/postgresql-8.4 restart
#~ # get the shmmax value from message
#~ sudo sysctl -w kernel.shmmax=4403486720 #(temporary)
#~ sudo nano /etc/sysctl.conf 
#~ kernel.shmmax=4403486720 #(permanent)
#~ sudo /etc/init.d/postgresql-8.4 restart
#~ time shp2pgsql -a -g way N06E124 contours | psql -U mapnik -q contour
#~ real	6m45.998s
#~ user	1m0.092s
#~ sys	0m16.669s
#~ => disk is the limiting factor?


#~ echo "ALTER TABLE contour ADD COLUMN contour3857 geometry(LINESTRING,3857);" | psql -d contours #(long 5h ??)
#~ echo "ALTER TABLE contour drop column contour3857;" | psql -d contours
#~ echo $(date) ": table dropped"
#~ echo "SELECT AddGeometryColumn ('contour','contour3857',3857,'LINESTRING',2, false);" | psql -d contours
#~ echo $(date) ": AddGeometryColumn done"
#~ echo "UPDATE contour SET contour3857=ST_Transform(wkb_geometry,3857);" | psql -d contours
#~ echo $(date) ": table updated"
echo "SELECT DropGeometryColumn ('contour','wkb_geometry');" | psql -d contours
echo $(date) ": DropGeometryColumn done"
#~ echo "CREATE INDEX contour3857_geom_idx ON contour USING gist (contour3857);" | psql -d contours pas nécessaire !
#~ echo date ": Index done"
