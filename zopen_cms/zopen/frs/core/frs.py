# -*- encoding:utf-8 -*-
""" vfs = virtual file system; a virtual posix like file system
"""

import os, shutil
import posixpath
from types import UnicodeType
from ConfigParser import SafeConfigParser
from StringIO import StringIO

# from zope.event import notify

from utils import ucopy2, ucopytree, umove

from manifest import ManifestMixin
from metadata import MetadataMixin
from archive import ArchiveSupportMixin
from recycle import RecycleMixin
from cache import CacheMixin

from events import *

def loadFRSFromConfig(config):
    """ load frs from config file """
    cp = SafeConfigParser()
    cp.readfp(StringIO(config))

    frs = FRS()
    cache_path = cp.get('cache', 'path')
    frs.setCacheRoot(unicode(cache_path))
    
    roots = cp.items('root')
    for name,path in roots:
        path = os.path.normpath(path)
        if not os.path.exists(path):
            os.makedirs(path)
        frs.mount(unicode(name), unicode(path))

    roots = cp.items('site')
    for site_path, vpath in roots:
        frs.mapSitepath2Vpath( unicode(site_path), unicode(vpath) )
    return frs

class FRS(MetadataMixin, ManifestMixin, ArchiveSupportMixin, RecycleMixin, CacheMixin):

    def __init__(self, cache_root='/tmp', dotfrs='.frs', version="json"):
        self._top_paths = {}
        self.dotfrs = dotfrs
        self.cache_root = cache_root
        self.sitepaths2vpaths = []
        self.version = version

    def mount(self, name, path):
        """ XXX only support mount top dirs only now

        mount filesystem path to vfs
        """
        if not os.path.exists(path):
            raise OSError('no mount path: '+ path)
        if name.startswith('/'):
            name = name[1:]
        self._top_paths[name] = path

    def mapSitepath2Vpath(self, site_path, vpath):
        """ map vpath to site path """
        self.sitepaths2vpaths.append( (site_path, vpath) )

    def sitepath2Vpath(self, site_path):
        if site_path[-1] != '/':
            site_path += '/'

        for _spath, _vpath in self.sitepaths2vpaths:
            if _spath[-1] != '/':
                _spath += '/'

            if site_path.startswith(_spath):
                if _vpath[-1] != '/':
                    _vpath += '/'

                result = _vpath + site_path[len(_spath):]
                if result[-1] == '/':
                    return result[:-1]
                return result
        raise ValueError('can not find a frs path for site path %s' % site_path)

    def setCacheRoot(self, path):
        """ where to push caches """
        self.cache_root = path

    def vpath(self, ospath):
        """ transform ospath to vpath """
        for root, path in self._top_paths.items():
            if ospath.startswith(path + '/'):
                return '/%s%s' % (root, ospath[len(path):])

    def ospath(self, vPath):
        """ transform to a real os path """
        if not vPath.startswith('/'):
            raise OSError(vPath)
        parts = vPath.split('/')
        try:
            toppath = self._top_paths[parts[1]]
        except KeyError:
            if parts[1] == self.dotfrs:
                try:
                    toppath = self._top_paths[parts[2]]
                except:
                    raise OSError(vPath)
                basename = os.path.basename(toppath)
                basedir = os.path.dirname(toppath)
                return os.path.join(basedir, self.dotfrs, basename, *parts[3:])
            raise OSError(vPath)
        return os.path.join(toppath, *parts[2:])

    def frspath(self, vpath, *frs_subpaths):
        """ It is another kind of joinpath, which returns path in the .frs folder.
        """
        return self.joinpath(self.dirname(vpath), \
                  self.dotfrs, self.basename(vpath), *frs_subpaths)

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

        names = [name for name in names if not name.startswith(self.dotfrs) ]
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

                if self.dotfrs in dirnames:
                    dirnames.remove(self.dotfrs)

                if dirnames or filenames:
                    dir_sub_path = dirpath[top_ospath_len+1:].replace(os.path.sep,  '/')
                    if dir_sub_path:
                        yield self.joinpath(top, dirpath[top_ospath_len+1:].replace(os.path.sep,  '/')), dirnames, filenames
                    else:
                        yield top, dirnames, filenames

    # asset management

    def removeAsset(self, path):
        frsPath = self.frspath(path)
        if self.exists(frsPath):
            self.rmtree(frsPath) 

        if self.exists(path):
            if self.isfile(path):
                self.remove(path)
            else:
                self.rmtree(path)

        CacheMixin.removeCache(self, path)

    def moveAsset(self, src, dst):
        """ rename or move a file or folder
        """
        frsSrc = self.frspath(src)
        if self.exists(frsSrc):
            frsDst = self.frspath(dst)
            if not self.exists( self.dirname(frsDst) ):
                self.makedirs(self.dirname(frsDst))
            self.move(frsSrc, frsDst )

        if not self.exists( self.dirname(dst) ):
            self.makedirs( self.dirname(dst) )
        self.move(src, dst)

        #if self.version == 'json':
        #  me = self.getMetadata(dst)
        #  # how to uid?
        #  #移动后文件的intid也改变了,这里把id置为0,将在其他地方以intid替换
        #  me.metadata['zope']['id'] = 0
        #  self.saveMetadata(dst, me.metadata )

        CacheMixin.moveCache(self, src, dst)

    def copyAsset(self, src, dst, copy_archiveinfo=False, **kw):
        """ copy folder / file and associated manifest/subfiles, not include archives

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

        # TODO : should be more generic, copy all file/folder except archived

        # copy manifest
        # generate new uid when copy
        if self.version == '':
            self.genManifestUID(dst, self.getManifest(src) )

            # copy subfiles too
            srcSubfolder = self.subfilespath(src)
            if self.exists(srcSubfolder):
                dstSubfolder = self.subfilespath(dst)
                m_dir_path = self.dirname(dstSubfolder)
                if not self.exists(m_dir_path):
                    self.makedirs(m_dir_path)
                self.copytree(srcSubfolder, dstSubfolder)
        elif self.version == 'json':
            srcMetadatapath = self.metadatapath(src)
            dstMetadatapath = self.metadatapath(dst)
            if self.exists(srcMetadatapath):
                m_dir_path = self.dirname(dstMetadatapath)
                if not self.exists(m_dir_path):
                    self.makedirs(m_dir_path)
                self.copyfile(srcMetadatapath,dstMetadatapath)

        # copy archiveinfo file
        if copy_archiveinfo:
            srcArchivePath = self.archiveinfopath(src)
            if self.exists(srcArchivePath):
                dstArchivePath = self.archiveinfopath(dst)
                m_dir_path = self.dirname(dstArchivePath)
                if not self.exists(m_dir_path):
                    self.makedirs(m_dir_path)
                self.copyfile(srcArchivePath, dstArchivePath)

        # copy cache
        CacheMixin.copyCache(self, src,dst)

    def fullcopyAsset(self, src, dst):
        """ copy a folder or a file, include archives

        keep stat
        """
        if self.isfile(src):
            self.copyfile(src, dst)
        else:
            self.copytree(src, dst)

        frsSrc = self.frspath(src)
        if self.exists(frsSrc):
            frsDst = self.frspath(dst)
            frsDstDir = self.dirname(frsDst)
            if not self.exists(frsDstDir ):
                self.makedirs(frsDstDir)
            self.copytree(frsSrc, frsDst )

