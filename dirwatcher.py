#!/usr/bin/python

import os
import hashlib
import pickle
import time
import shutil
import argparse
import sys

BLOCK = 2**16 # for reading file chunks
KEYNOTFOUND = '<KEYNOTFOUND>'

def hash_file(path):
    '''Compute the hash of a file specified by the full path to it'''
    f = open(path, 'rb')
    digest = hashlib.md5()
    chunk = f.read(BLOCK)
    while len(chunk):
        digest.update(chunk)
        chunk = f.read(BLOCK)
    f.close()
    return digest.hexdigest()



def build_tree(path, exceptions=None, maxsize=None):
    result = {}
    for dirName, subDirs, files in os.walk(path, topdown=True):
        # remove ignored directories, if necessary
        if exceptions:
            for item in exceptions:
                if item in subDirs:
                    subDirs.remove(item)

        # add found files to index
        for item in files:
            fullPath = os.path.join(dirName, item)
            if os.path.isfile(fullPath):
                size = os.path.getsize(fullPath)
                if maxsize and size > maxsize:
                    # print 'skipping ', fullPath
                    continue
                fingerprint = hash_file(fullPath)
                result[fullPath] = fingerprint
            # otherwise it is a symlink, we skip it



    return result


def print_tree(data):
    for key, value in data.iteritems():
        print '%s\t%s' % (value, key)


def dump_tree(obj, path):
    '''Store the directory tree and hashes in a pickle at the given path'''
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

def get_tree(path):
    '''Load a directory tree and accompanying hashes from a pickle
    produced at the previous run'''
    with open(path, 'rb') as f:
        obj = pickle.load(f)
    return obj


def dict_diff(first, second):
    """ Return a dict of keys that differ with another config object.  If a value is
        not found in one fo the configs, it will be represented by KEYNOTFOUND.
        @param first:   Fist dictionary to diff.
        @param second:  Second dicationary to diff.
        @return diff:   Dict of Key => (first.val, second.val)
    """
    diff = {}
    # Check all keys in first dict
    for key in first.keys():
        if key not in second:
            diff[key] = (first[key], KEYNOTFOUND)
        elif first[key] != second[key]:
            diff[key] = (first[key], second[key])
    # Check all keys in second dict to find missing
    for key in second.keys():
        if key not in first:
            diff[key] = (KEYNOTFOUND, second[key])
    return diff

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Full path to directory to scan', type=str)
    parser.add_argument('--store', help='Directory for storage of state between runs',
                        type=str, default='~/.dirwalker')
    parser.add_argument('-i', '--ignore', help='Comma-separated list of entries to ignore',
                        nargs='*', default=None)
    parser.add_argument('--maxsize', help='Only hash files smaller than this many BYTES',
                        type=int, default=None)


    args = parser.parse_args()

    PATH = args.path
    IGNORE = args.ignore
    timestamp = time.strftime('%Y-%d-%m-%H-%M-%S')

    if not os.path.exists(args.store):
        os.makedirs(args.store)
    os.chdir(args.store)

    try:
        original = get_tree('canonical.tree')
    except IOError, err:
        print err
        print 'no original tree exists, building it'
        print 'this will take a while'
        tree = build_tree(PATH, IGNORE, args.maxsize)
        dump_tree(tree, 'canonical.tree') #will be subsequently updated
        dump_tree(tree, 'canonical.tree-start-point') #always constant
        print 'Done, quitting.'
        sys.exit(0)
    else:
        # we've found an earlier tree, let's build a new one and compare
        # we're not printing anything to stdout, not to cause unnecessary emails
        # sent by cron; we print only if the admin's attention is required
        currentTree = build_tree(PATH, IGNORE, args.maxsize)
        delta = dict_diff(original, currentTree)
        if delta:
            dump_tree(currentTree, '%s.tree' % timestamp)
            print 'Differences found: ', len(delta)
            print_tree(delta)

            # the output of the cronjob will be sent by email
            # to avoid duplicate notifications, make the current
            # tree the original
            os.unlink('canonical.tree')
            shutil.copy('%s.tree' % timestamp, 'canonical.tree')
            os.rename('%s.tree' % timestamp, 'canonical.tree')
            print 'Done'
        else:
            # no changes were detected
            pass
