#!/usr/bin/python

import os
import sqlite3

class SqliteTileStorage():
	""" Sqlite files methods for simple tile storage"""

	def __init__(self, type):
		self.type=type
	
	def create(self, filename, overwrite=False):
		""" Create a new storage file, overwrite or not if already exists"""
		self.filename=filename
		CREATEINDEX=True
		
		if overwrite:
			if os.path.isfile(self.filename):
				os.unlink(self.filename)
		else:
			if os.path.isfile(self.filename):
				CREATEINDEX=False
				
		self.db = sqlite3.connect(self.filename)
		
		cur = self.db.cursor()
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
				desc TEXT,
				tilenumbering TEXT,
				minzoom int,
				maxzoom int)
			""")
		
		if CREATEINDEX:
			cur.execute(
				"""
				CREATE INDEX IND
				ON tiles(x,y,z,s)
				""")
				
		cur.execute("insert into info(desc) values('Simple sqlite tile storage..')")
		
		cur.execute("insert into info(tilenumbering) values(?)",(self.type,))
		
		self.db.commit()
		
	def open(self, filename) :
		""" Open an existing file"""
		self.filename=filename
		if os.path.isfile(self.filename):
			self.db = sqlite3.connect(self.filename)
			return True
		else:
			return False
			
	def writeImageFile(self, x, y, z, f) :
		""" write a single tile from a file """
		cur = self.db.cursor()
		cur.execute('insert into tiles (z, x, y,s,image) \
						values (?,?,?,?,?)',
						(z, x, y, 0, sqlite3.Binary(f.read())))
		self.db.commit()
		
	def writeImage(self, x, y, z, image) :
		""" write a single tile from string """
		cur = self.db.cursor()
		cur.execute('insert into tiles (z, x, y,s,image) \
						values (?,?,?,?,?)',
						(z, x, y, 0, sqlite3.Binary(image)))
		self.db.commit()
		
	def readImage(self, x, y, z) :
		""" read a single tile as string """
		
		cur = self.db.cursor()
		cur.execute("select image from tiles where x=? and y=? and z=?", (x, y, z))
		res = cur.fetchone()
		if res:
			print "found one tile"
			image = str(res[0])
			return image
		else :
			print "None found"
			return None
		
	def createFromDirectory(self, filename, basedir, overwrite=False) :
		""" Create a new sqlite file from a z/y/x.ext directory structure"""
		
		ls=os.listdir(basedir)
		
		self.create(filename, overwrite)
		cur = self.db.cursor()
		
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
					cur.execute('insert into tiles (z, x, y,image) \
								values (?,?,?,?)',
								(z, x, y,  sqlite3.Binary(f.read())))
								
	def createBigPlanetFromTMS(self, targetname, overwrite=False):
		""" Create a new sqlite with BigPlanet numbering scheme from a TMS one"""
		target=SqliteTileStorage('BigPlanet')
		target.create(targetname, overwrite)
		cur = self.db.cursor()
		cur.execute("select x, y, z from tiles")
		res = cur.fetchall()
		for (x, y, z) in res:
			xx= x
			zz= 17 - z
			yy= 2**zz - y -1
			im=self.readImage(x,y,z)
			target.writeImage(xx,yy,zz,im)
		
	def createTMSFromBigPlanet(self, targetname, overwrite=False):
		""" Create a new sqlite with TMS numbering scheme from a BigPlanet one"""
		target=SqliteTileStorage('TMS')
		target.create(targetname, overwrite)
		cur = self.db.cursor()
		cur.execute("select x, y, z from tiles")
		res = cur.fetchall()
		for (x, y, z) in res:
			xx= x
			zz= 17 - z
			yy= 2**zz - y -1
			im=self.readImage(x,y,z)
			target.writeImage(xx,yy,zz,im)
	
	def createTMSFromOSM(self, targetname, overwrite=False):
		""" Create a new sqlite with TMS numbering scheme from a OSM/Bing/Googlemaps one"""
		target=SqliteTileStorage('TMS')
		target.create(targetname, overwrite)
		cur = self.db.cursor()
		cur.execute("select x, y, z from tiles")
		res = cur.fetchall()
		for (x, y, z) in res:
			xx= x
			zz= z
			yy= 2**zz - y
			im=self.readImage(x,y,z)
			target.writeImage(xx,yy,zz,im)
	
	def createOSMFromTMS(self, targetname, overwrite=False):
		""" Create a new sqlite with OSM/Bing/Googlemaps numbering scheme from a TMS one"""
		target=SqliteTileStorage('OSM')
		target.create(targetname, overwrite)
		cur = self.db.cursor()
		cur.execute("select x, y, z from tiles")
		res = cur.fetchall()
		for (x, y, z) in res:
			xx= x
			zz= z
			yy= 2**zz - y
			im=self.readImage(x,y,z)
			target.writeImage(xx,yy,zz,im)
		
#store=SqliteTileStorage('TMS')
#store.open('N45E006.sqlitedb')
#store.createBigPlanetFromTMS('bp.sqlitedb',True)

