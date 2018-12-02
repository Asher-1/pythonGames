from distutils.core import setup, Extension
try:
	import py2exe
except:
	pass
		
import sys
import glob
import os
import shutil

#NOTE: in the .iss file
#add
#WorkingDir: "{app}"
#after the exe in Icons (2 times) and Run (just once)

#NOTE: also py2exe uses the pyc's that are installed in
#c:\python\libs\site-packages
#and then caches them in ./build/...
#so be careful if you are bundling a lib, but have an old version
#hanging about in your site-packages

cmd = sys.argv[1]

data = [
	os.path.join("data","explosion","*"),
	os.path.join("data","fonts","*"),
	os.path.join("data","gfx","*"),
	os.path.join("data","levels","*"),
	os.path.join("data","music","*"),
	os.path.join("data","player","*"),
	os.path.join("data","sfx","*"),
	os.path.join("data","soldier","*"),
	'icon*',
	'hs.dat*',
	'tileedit.ini', #i guess.
	'dynamite',
	'*.txt',
	]
src = [
	'*.py',
	'*.c',
	'*.h',
	'*.i',
	os.path.join("pgu","*.py"),
	]

if cmd in ('sdist'): 
	f = open("MANIFEST.in","w")
	for l in data: f.write("include "+l+"\n")
	for l in src: f.write("include "+l+"\n")
	f.close()
	
		
if cmd in ('sdist','build'):
	setup(
		name='dynamite',
		version='1.1',
		description="The evil potentate is ruining everyone's lives!  Use the power of dynamite to destroy his strongholds.",
		author='Phil Hassey',
		author_email='philhassey@yahoo.com',
		url='http://www.imitationpickles.org/pyweek1/',
		)

if cmd in ('py2exe',):
	setup(
		options={'py2exe':{
			'dist_dir':'dist',
			'dll_excludes':['_dotblas.pyd','_numpy.pyd']
			}},
		windows=[{
			'script':'dynamite.py',
			'icon_resources':[(1,'icon.ico')],
			}],
		)
		
if cmd in ('build',):
	for fname in glob.glob("build/lib*/*.so"):
		shutil.copy(fname,os.path.basename(fname))
		
	for fname in glob.glob("build/lib*/*.pyd"):
		shutil.copy(fname,os.path.basename(fname))
		
	
if cmd in ('py2exe',):
	for gname in data:
		for fname in glob.glob(gname):
			dname = os.path.join('dist',os.path.dirname(fname))
			try: 
				#os.mkdir(dname)
				os.makedirs(dname)
			except:
				'mkdir failed: '+dname
			shutil.copy(fname,dname)
	