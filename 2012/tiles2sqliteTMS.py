#!/usr/bin/python

import math
import os, pdb
import re
#from tile_utils import TileNames
import sqlite3

# createdb
db = sqlite3.connect('srtm-filled-hillshade.sqlitedb')
cur = db.cursor()
cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tiles (
            x int,
            y int,
            z int, 
            s int,
            image blob,
            PRIMARY KEY(x,y,z,s))
        """)
cur.execute(
        """
        CREATE TABLE IF NOT EXISTS info (
            minzoom int,
            maxzoom int)
        """)
cur.execute(
        """
        CREATE TABLE IF NOT EXISTS android_metadata (
            locale TEXT)
        """)
cur.execute(
        """
        CREATE INDEX IND
        ON tiles(x,y,z,s)
        """)


basedir=os.path.abspath('tiles/')
print basedir
ls=os.listdir(basedir)

for zs in os.listdir(basedir):
	zz=int(zs)
	for xs in os.listdir(basedir+'/'+zs+'/'):
		xx=int(xs)
		for ys in os.listdir(basedir+'/'+zs+'/'+'/'+xs+'/'):
			yy=int(ys.split('.')[0])
			print zz, yy, xx
			z=zz
			x=xx
			y=yy
			print basedir+'/'+zs+'/'+'/'+xs+'/'+ys
			f=open(basedir+'/'+zs+'/'+'/'+xs+'/'+ys)
			cur.execute('insert into tiles (z, x, y,s,image) \
						values (?,?,?,?,?)',
						(z, x, y, 0, sqlite3.Binary(f.read())))

db.commit()

#pdb.set_trace()

#cursor.execute('insert into File (id, name, bin) values (?,?,?)', (id, name, sqlite3.Binary(file.read())))

