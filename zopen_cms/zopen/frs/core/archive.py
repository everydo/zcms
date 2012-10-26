# -*- encoding: utf-8 -*-
""" asset archive management
"""
import time
from xml.sax import parseString, ContentHandler
from xml.sax.saxutils import escape

from utils import timetag
from config import FRS_ARCHIVED_FOLDER_NAME, FRS_ARCHIVE_INFO_FILE_NAME

from string import Template

archive_template = Template("""<?xml version="1.0" ?>
<archive xmlns="http://zopechina.com/ns/frs"
         id = "$id"
         filename="$filename"
         actor="$actor"
         size = "$size"
         content_type = "$content_type"
         version_number="$version_number"
         revision_number="$revision_number"
         time="$time"><![CDATA[$comment]]></archive>
""")

class ArchiveInfo:

    def __init__(self, id='', **kw):
        self.id = id
        self.archive = kw
        self.archive['id'] = id
        self.archive['size'] = kw.get('size', 0)
        self.archive['comment'] = kw.get('comment', '')
        self.archive['actor'] = 'users.admin'
        self.archive['time'] = kw.get('time', time.strftime('%Y-%m-%d %H:%M:%S'))
        self.archive['version_number'] = kw.get('version_number', '1')
        self.archive['revision_number'] = kw.get('revision_number', '0')
        self.archive['filename'] = kw.get('filename', '')

    def load(self, manifest_body):
        print 'loading archive info ........................'
        parser = ArchiveParser(self)
        parseString( manifest_body, parser)

    def write2xml(self, stream):
        kw = dict(self.archive)
        kw['filename'] = escape(kw['filename'])
        kw['comment'] = escape(kw['comment'])
        xml_str = archive_template.substitute(**kw)
        stream.write(xml_str.encode('utf8'))

class ArchiveParser( ContentHandler ):
    
    def __init__(self, archiveinfo=None):
        self._ai = archiveinfo or ArchiveInfo()
        self._chars = []

    def getArchiveInfo(self):
        return self._ai

    def startElement(self, name, attrs):
        if name == 'archive':
            self._ai.archive['actor'] = attrs.get('actor', '')
            self._ai.archive['time'] = attrs.get('time', '')
            self._ai.archive['filename'] = attrs.get('filename', '')
            self._ai.archive['id'] = attrs.get('id', '')
            self._ai.archive['size'] = int(attrs.get('size', 0))
            self._ai.archive['version_number'] = attrs.get('version_number', '')
            self._ai.archive['revision_number'] = attrs.get('revision_number', '')
            self._ai.archive['content_type'] = attrs.get('content_type', '')

    def endElement( self, name ):
        if name == 'archive':
            self._ai.archive['comment'] = "".join(self._chars).strip()
        self._chars = []

    def characters( self, buffer ):
        self._chars.append( buffer )

class ArchiveSupportMixin:

    def archivedpath(self, path, *args):
        return self.frspath(path, FRS_ARCHIVED_FOLDER_NAME, *args)

    def archiveinfopath(self, path):
        return self.frspath(path, FRS_ARCHIVE_INFO_FILE_NAME)

    def archive(self, path, id=None, **archiveInfo):
        archivePath = self.archivedpath(path)
        if not self.exists(archivePath):
            self.makedirs(archivePath)

        if not id:
            ext = self.splitext(path)[-1]
            id = timetag() + ext
        dstpath = self.joinpath(archivePath, id)
        self.copyAsset(path, dstpath, copycache=0, copy_archiveinfo=0)
        ai = ArchiveInfo(id=id, filename=self.basename(path), **archiveInfo)

        # 版本信息目录
        ai_path_folder = self.frspath(self.archivedpath(path, id))
        if not self.exists(ai_path_folder):
            self.makedirs(ai_path_folder)

        # 版本信息文件
        ai_path = self.archiveinfopath(self.archivedpath(path, id))
        ai.write2xml(open(self.ospath(ai_path), 'w'))

    def listArchives(self, path):
        archivePath = self.archivedpath(path)
        if self.exists(archivePath):
            archives = self.listdir(archivePath)
        else:
            archives = []
        return archives

    def getArchiveInfo(self, path, archivename):
        if archivename == '':
            ai_path = self.archiveinfopath(path)
        else:
            ai_path = self.archiveinfopath(self.archivedpath(path, archivename))
        ai = ArchiveInfo(id=archivename)
        try:
            ai.load(open(self.ospath(ai_path)).read() )
        except IOError:
            pass
        return ai.archive

    def copyArchive(self, path, archiveName, dstPath):
        assetpath = self.archivedpath(path, archiveName)
        return self.copyAsset(assetpath, dstPath, copycache=0, copy_archiveinfo=0)

    def removeArchive(self, path, archiveName):
        self.removeAsset( self.archivedpath(path, archiveName) )

if __name__ == '__main__':
    ai = ArchiveInfo(id='asdfasdfas', time='2003-12-23', actor='panjy', comment='asdjas asd f as df', filename='aa.txt',version_number='1',revision_number='2',size='888')
    from StringIO import StringIO
    stream = StringIO()
    ai.write2xml(open('sample-archive-info.xml', 'w'))

    print stream.getvalue()
    ai = ArchiveInfo(id='asdfasdfas')
    ai.load(open('sample-archive-info.xml').read())
    print ai.archive

