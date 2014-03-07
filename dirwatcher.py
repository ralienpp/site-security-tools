#!/home7/raileann/opt/python27/bin/python

import os
import hashlib
import pickle
import time
import shutil

BLOCK = 2**16 #for reading file chunks

def HashFile(path):
	f = open(path, 'rb')
	digest = hashlib.md5()
	chunk = f.read(BLOCK)
	while len(chunk):
		digest.update(chunk)
		chunk = f.read(BLOCK)
	f.close()
	return digest.hexdigest()
	


def BuildTree(path, exceptions=[]):
	tree = {}
	for dirName, subDirs, files in os.walk(path):
		#add found files to index
		for item in files:
			fullPath = os.path.join(dirName, item)
			fingerprint = HashFile(fullPath)
			tree[fullPath] = fingerprint

		#remove ignored directories, if necessary
		for item in exceptions:
			if item in subDirs:
				subDirs.remove(item)

	return tree


def PrintTree(tree):
	for key, value in tree.iteritems():
		print '%s\t%s' % (value, key)


def CompareTrees(new, original):
	'''Returns keys present in new, but not present in original'''
	delta = set(new.keys()) - set(original.keys())
	return delta

def DumpTree(obj, path):
	with open(path, 'wb') as f:
		pickle.dump(obj, f)

def GetTree(path):
	with open(path, 'rb') as f:
		obj=pickle.load(f)
	return obj
	
'''def dict_diff(d1, d2, NO_KEY='<KEYNOTFOUND>'):
	both = set(d1.keys()) & set(d2.keys())
	diff = {k:(d1[k], d2[k]) for k in both if d1[k] != d2[k]}
	diff.update({k:(d1[k], NO_KEY) for k in d1.keys() - both})
	diff.update({k:(NO_KEY, d2[k]) for k in d2.keys() - both})
	return diff
'''
def dict_diff(first, second):
	""" Return a dict of keys that differ with another config object.  If a value is
		not found in one fo the configs, it will be represented by KEYNOTFOUND.
		@param first:   Fist dictionary to diff.
		@param second:  Second dicationary to diff.
		@return diff:   Dict of Key => (first.val, second.val)
	"""
	KEYNOTFOUND = '<KEYNOTFOUND>'
	diff = {}
	# Check all keys in first dict
	for key in first.keys():
		if (not second.has_key(key)):
			diff[key] = (first[key], KEYNOTFOUND)
		elif (first[key] != second[key]):
			diff[key] = (first[key], second[key])
	# Check all keys in second dict to find missing
	for key in second.keys():
		if (not first.has_key(key)):
			diff[key] = (KEYNOTFOUND, second[key])
	return diff

if __name__ == '__main__':
	PATH='/home7/raileann/public_html/__lazybit'#'/home/alex/workspace'
	IGNORE=['cache']
	timestamp = time.strftime('%Y-%d-%m-%H-%M-%S')

	os.chdir('/home7/raileann/opt/walker')

	#import pdb
	try:
		original = GetTree('canonical.tree')
		#print 'Found tree, comparing delta'
		currentTree = BuildTree(PATH, IGNORE)
		#newFiles = CompareTrees(currentTree, original)
		#if newFiles:
		#	DumpTree(tree, '%s.tree' % timestamp)
		#	print 'New files found'
		#	print newFiles

		delta = dict_diff(original, currentTree)
		if delta:
			DumpTree(currentTree, '%s.tree' % timestamp)
			print 'Differences found: ', len(delta.items())
			PrintTree(delta)

			#the output of the cronjob will be sent by email
			#to avoid duplicate notifications, make the current
			#tree the original
			os.unlink('canonical.tree')
			shutil.copy('%s.tree' % timestamp, 'canonical.tree')
			os.rename('%s.tree' % timestamp, 'canonical.tree')
			print 'Done'
		else:
			pass #print 'No changes'
	
		
	except Exception, err:
		print err
		print 'no original tree exists, building it'
		print 'this will take a while'
		tree = BuildTree(PATH, IGNORE)
		DumpTree(tree, 'canonical.tree') #will be subsequently updated
		DumpTree(tree, 'canonical.tree-start-point') #always constant
		print 'Done\n\n'
		#PrintTree(tree)


