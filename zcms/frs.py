# -*- encoding:utf-8 -*-
""" vfs = virtual file system; a virtual posix like file system
"""

import os, shutil
import posixpath
from types import UnicodeType
import yaml
import time
import sys
import fnmatch

FS_CHARSET = sys.getfilesystemencoding()

def ucopytree(ossrc, osdst, symlinks=False):
    # ucopy2 dosn't work with unicode filename yet
    if type(osdst) is UnicodeType and \
            not os.path.supports_unicode_filenames:
        ossrc = ossrc.encode(FS_CHARSET)
        osdst = osdst.encode(FS_CHARSET)
    shutil.copytree(ossrc, osdst, symlinks)

def umove(ossrc, osdst):
    # umove dosn't work with unicode filename yet
    if type(osdst) is UnicodeType and \
           not os.path.supports_unicode_filenames:
        ossrc = ossrc.encode(FS_CHARSET)
        osdst = osdst.encode(FS_CHARSET)
    shutil.move(ossrc, osdst)

class FRS:

    def __init__(self, cache_root='/tmp'):
        self._top_paths = {}
        self.cache_root = cache_root

    def mount(self, name, path):
        """ XXX only support mount top dirs only now

        mount filesystem path to vfs
        """
        if not os.path.exists(path):
            raise OSError('no mount path: '+ path)
        if name.startswith('/'):
            name = name[1:]
        self._top_paths[name] = path

    def setCacheRoot(self, path):
        """ where to push caches """
        self.cache_root = path

    def vpath(self, ospath):
        """ transform ospath to vpath """
        for root, path in self._top_paths.items():
            if ospath.startswith(path + '/'):
                return '/%s%s' % (root, ospath[len(path):])

    def cache_path(self, vpath):
        """ get os path of cache folder for vpath """
        return os.path.join(self.cache_root, 
                            *vpath.split('/') )

    def ospath(self, vPath):
        """ transform to a real os path """
        if not vPath.startswith('/'):
            raise OSError(vPath)
        parts = vPath.split('/')
        toppath = self._top_paths[parts[1]]
        return os.path.join(toppath, *parts[2:])

    def exists(self, vPath):
        try:
            path = self.ospath(vPath)
        except OSError:
            return False
        return os.path.exists(path)

    def joinpath(self, *arg):
        return posixpath.join(*arg)

    def basename(self, path):
        return posixpath.basename(path)

    def splitext(self, name):
        return os.path.splitext(name)

    def stat(self, vPath):
        return os.stat(self.ospath(vPath))

    def dirname(self, path):
        return posixpath.dirname(path)

    def ismount(self, vPath):
        """ return if vPath is a mount folder
        """
        return vPath[1:] in self.listdir('/')

    def isdir(self, vPath):
        return os.path.isdir(self.ospath(vPath))

    def isfile(self, vPath):
        return os.path.isfile(self.ospath(vPath))

    def atime(self, vPath):
        return os.path.getatime( self.ospath(vPath) )

    def mtime(self, vPath):
        return os.path.getmtime( self.ospath(vPath) )

    def ctime(self, vPath):
        return os.path.getctime( self.ospath(vPath) )

    def getsize(self, vPath):
        return os.path.getsize( self.ospath(vPath) )

    def listdir(self, vPath, pattern=None):
        if vPath == '/':
             return self._top_paths.keys()
        names = os.listdir(self.ospath(vPath))
        if pattern is not None:
            names = fnmatch.filter(names, pattern)
        return names

    def dirs(self, vPath, pattern=None):
        names = [ name for name in self.listdir(vPath, pattern)\
	                  if self.isdir(self.joinpath(vPath, name))]
        return names

    def files(self, vPath, pattern=None):
        names = [ name for name in self.listdir(vPath, pattern)\
	                  if self.isfile(self.joinpath(vPath, name))]
        return names

    def open(self, vPath, mode='r'):
        return file(self.ospath(vPath), mode)

    def move(self, vPath1, vPath2):
        # can't remove mount folder
        if self.ismount(vPath1):
            raise Exception("can't remove mount folder %s" % vPath1)
        if self.ismount(vPath2):
            raise Exception("can't move to mount folder %s" % vPath2)

        umove(self.ospath(vPath1), self.ospath(vPath2) )
        #notify(AssetMoved(self, vPath1, vPath2))

    def mkdir(self, vPath, mode=0777):
        os.mkdir(self.ospath(vPath), mode)

    def makedirs(self, vPath, mode=0777):
        os.makedirs(self.ospath(vPath), mode)

    def getNewName(self, path, name):
        while self.exists(self.joinpath(path, name)):
            name = 'copy_of_' + name
        return name

    def remove(self, vPath):
        """ remove a file path"""
        os.remove(self.ospath(vPath) )
        #notify(AssetRemoved(self, vpath))

    def copyfile(self, vSrc, vDst):
        shutil.copyfile(self.ospath(vSrc), self.ospath(vDst))

    def copytree(self, vSrc, vDst):
        # copy2 don't work well with encoding
        # in fact it is os.utime don't work well
        ossrc = self.ospath(vSrc)
        osdst = self.ospath(vDst)
        ucopytree(ossrc, osdst, symlinks=False)

    def rmtree(self, vPath, ignore_errors=False, onerror=None):
        # can't remove mount folder
        if self.ismount(vPath):
            raise Exception("can't remove mount folder %s" % vPath)

        shutil.rmtree(self.ospath(vPath), ignore_errors, onerror)

    def touch(self, vpath):
        fd = os.open(self.ospath(vpath), os.O_WRONLY | os.O_CREAT, 0666)
        os.close(fd)

    def walk(self, top, topdown=True, onerror=None):
        if top == '/':
            mount_dirs = self._top_paths.keys()
            yield '/', mount_dirs,[]
            for name in mount_dirs:
                for item in self.walk('/' + name, topdown, onerror):
                    yield item
        else:
            top_ospath = os.path.normpath(self.ospath(top))
            top_ospath_len = len(top_ospath)
            for dirpath, dirnames, filenames in os.walk(top_ospath,topdown,onerror):

                if dirnames or filenames:
                    dir_sub_path = dirpath[top_ospath_len+1:].replace(os.path.sep,  '/')
                    if dir_sub_path:
                        yield self.joinpath(top, dirpath[top_ospath_len+1:].replace(os.path.sep,  '/')), dirnames, filenames
                    else:
                        yield top, dirnames, filenames

    # asset management

    def removeAsset(self, path):
        if self.exists(path):
            if self.isfile(path):
                self.remove(path)
            else:
                self.rmtree(path)

        os.remove(self.cache_path(path))

    def moveAsset(self, src, dst):
        """ rename or move a file or folder
        """
        if not self.exists( self.dirname(dst) ):
            self.makedirs( self.dirname(dst) )
        self.move(src, dst)

        cache_src = self.cache_path(src)
        if not os.path.exists(cache_src):
            return 

        cache_dst = self.cache_path(dst)
        if not os.path.exists( os.path.dirname(cache_dst) ):
            os.makedirs( os.path.dirname(cache_dst) )
        shutil.move(cache_src, cache_dst)

    def copyAsset(self, src, dst, **kw):
        """ copy folder / file 

        don't keep stat
        """
        if self.isfile(src):
            self.copyfile(src, dst)
        else:
            # copy folder
            if not self.exists(dst):
                self.makedirs(dst)
            for name in self.listdir(src):
                self.copyAsset(self.joinpath(src, name), self.joinpath(dst, name), copycache=0)

        # copy cache
        cache_src = self.cache_path(src)
        if not os.path.exists(cache_src):
            return

        cache_dst = self.cache_path(dst)
        cache_dst_parent = os.path.dirname(cache_dst)
        if not os.path.exists( cache_dst_parent ):
            os.makedirs(cache_dst_parent )
        if not os.path.exists(cache_dst):
            ucopytree(cache_src, cache_dst)

