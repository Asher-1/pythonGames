"""
Record ID - 
in dynamite

"phil-1"
"buck-2"
"_high-1",


in a normal game

"easy"
"medium"
"hard"

or in a game with no settings

"high"

..

data stored in a dict

{'phil-1':[array of tuples]}

so...

High['easy'] will give back an array of tuples of the highs
(1234,'buck',other data,etc.etc)

data stored in text file

id, score, name, data

highs = high.Highs("hs.dat",10)

top10 = highs['default']

#or just
top10 = high.Highs('hs.dat')['default']

#or just
top10 = high.High("hs.data") #shortcut for above line

place = top10.submit( 495,'buck',sort=-1,optionaldataxxx) => returns placing, None if no place.  not overly pythonic, but, whatever.

top10[place].name = 'buck2' #they type in their name

for e in top10:
	blah blah
	print e.name,e.score,e.data
	
top10.save() 
highs.save()

highs.load() #to re-load the data, 
"""

import os

def High(fname,limit=10):
	return Highs(fname,limit)['default']
	
class _Score:
	def __init__(self,score,name,data=None):
		self.score,self.name,self.data=score,name,data
	
class _High:
	def __init__(self,highs,limit=10):
		self.highs = highs
		self._list = []
		self.limit = limit
		
	def save(self):
		self.highs.save()
		
	def submit(self,score,name,data=None):
		n = 0
		for e in self._list:
			if score > e.score:
				self._list.insert(n,_Score(score,name,data))
				self._list = self._list[0:self.limit]
				return n
		if len(self._list) < self.limit:
			self._list.append(_Score(score,name,data))
			return len(self._list)-1
	
	def check(self,score):
		n = 0
		for e in self._list:
			if score > e.score:
				return n
		if len(self._list) < self.limit:
			return len(self._list)
		
		
	def __iter__(self):
		return self._list.__iter__()
		
	def __getitem__(self,key):
		return self._list[key]
		
	def __len__(self):
		return self._list.__len__()
		

class Highs:
	def __init__(self,fname,limit=10):
		self.fname = fname
		self.limit = limit
		self.load()
		
	def load(self):
		self._dict = {}
		try:
			f = open(self.fname)
			for line in f.readlines():
				key,score,name,data = line.strip().split("\t")
				if key not in self._dict:
					self._dict[key] = _High(self,self.limit)
				high = self._dict[key]
				high.submit(int(score),name,data)
			f.close()
		except:
			pass
	
	def save(self):
		f = open(self.fname,"w")
		for key,high in self._dict.items():
			for e in high:
				f.write("%s\t%d\t%s\t%s\n"%(key,e.score,e.name,str(e.data)))
		f.close()
		
	def __getitem__(self,key):
		if key not in self._dict:
			self._dict[key] = _High(self,self.limit)
		return self._dict[key]
		

"""
highs = Highs("hs.dat")
high = highs['default']
high.submit(100,'phil')
high.submit(200,'phil')
high.submit(300,'phil')
for e in high:
	print e.score,e.name,e.data
highs.save()

high = High("mini.dat")
n = high.submit(100,'phil')
#high[n].score = 125
#high[n].name = 'buck'
high.save()
for e in high:
	print e.score,e.name,e.data
	
highs = Highs("hs2.dat")
for i in range(1,10):
	highs[str(i)].submit(i*32,'buck')
highs.save()
"""