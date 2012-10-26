import os
import shutil

from config import FRS_CACHE_FOLDER_PREFIX
from utils import ucopytree

class CacheMixin:

    def getCacheFolder(self, vpath, cachename=None):
        """ get os path of cache folder for vpath """
        cachebase = os.path.join(self.cache_root, 
                            *vpath.split('/') )
        if cachename:
            foldername = FRS_CACHE_FOLDER_PREFIX + cachename
            return os.path.join(cachebase, foldername)
        else:
            return cachebase

    def getCacheDecompress(self, vpath, cachename=None):
        """ get os path of cache decompress for vpath """
        return os.path.join(self.getCacheFolder(vpath, cachename), 'decompress')

    def getCacheDecompressPreview(self, vpath, cachename=None):
        """ get os path of cache decompress preview for vpath """
        return os.path.join(self.getCacheFolder(vpath, cachename), 'decompresspreview')

    def hasCache(self, vpath, cachename=None):
        return os.path.exists(self.getCacheFolder(vpath, cachename))


    def removeCache(self, vpath,cachename=None):
        path = self.getCacheFolder(vpath, cachename)
        if os.path.exists(path):
            shutil.rmtree( path )

    def moveCache(self, src, dst):
        cache_src = self.getCacheFolder(src)
        if not os.path.exists(cache_src):
            return 

        cache_dst = self.getCacheFolder(dst)

        if not os.path.exists( os.path.dirname(cache_dst) ):
            os.makedirs( os.path.dirname(cache_dst) )
        shutil.move(cache_src, cache_dst)

    def copyCache(self, src, dst, **kw):
        cache_src = self.getCacheFolder(src)
        if not os.path.exists(cache_src):
            return

        cache_dst = self.getCacheFolder(dst)

        cache_dst_parent = os.path.dirname(cache_dst)
        if not os.path.exists( cache_dst_parent ):
            os.makedirs(cache_dst_parent )
        if not os.path.exists(cache_dst):
            ucopytree(cache_src, cache_dst)

