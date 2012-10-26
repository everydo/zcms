""" read and write the manifest file """

from xml.sax import parseString, ContentHandler
from string import Template
from config import SUB_FILES_FOLDER_NAME
from utils import make_uuid

class ManifestMixin:
    def manifestpath(self, vpath):
        return self.frspath(vpath, 'manifest.xml')

    def getManifest(self, vpath):
        mi = Manifest()
        manifestpath = self.manifestpath(vpath)
        if self.exists(manifestpath):
            mi.load( open(self.ospath(manifestpath)).read() )
        return mi

    def saveManifest(self, vpath, manifest):
        """ set a property for a file of folder
        """
        manifestpath = self.manifestpath(vpath)

        folderpath = self.dirname(manifestpath)
        if not self.exists(folderpath):
            self.makedirs( folderpath )

        f = self.open(manifestpath, 'w')
        manifest.write2xml(f)
        f.close()

    # for subfiles in .frs folder
    def subfilespath(self, vpath, *subfilename):
        return self.frspath(vpath, SUB_FILES_FOLDER_NAME, *subfilename)

    def genManifestUID(self, vpath, manifest=None):
        if not manifest:
            manifest = Manifest()
        manifest.uid = make_uuid()
        self.saveManifest(vpath, manifest)

manifest_template = Template("""<?xml version="1.0" ?>
<manifest xmlns="http://zopechina.com/ns/frs"
           xmlns:tal="http://xml.zope.org/namespaces/tal"
           contenttype="$contenttype"
           uid="$uid">

$items

</manifest>
""")

manifest_item_template = Template("""
    <entry type="$type"
           name="$name"
           mimetype="$mimetype"
           filename="$filename"
           fullpath="$fullpath"/>
""")

class Manifest(object):

    def __init__(self, contenttype='', uid=''):
        self.contenttype = contenttype
        self.uid = uid
        self.manifest = []

    def appendFileEntry(self, **kw):
        self.manifest.append(kw)

    def getFileEntry(self, field_name):
        for entry in self.manifest:
            if entry.get('name', '') == field_name:
                return entry

    def load(self, manifest_body):
        parser = ManifestParser(self)
        parseString( manifest_body, parser)
       
    def write2xml(self, stream):
        items = []
        for item in self.manifest:
            items.append(manifest_item_template.substitute(**item))

        xml_str = manifest_template.substitute(contenttype=self.contenttype,
                              uid = self.uid,
                              items='\n'.join(items), )

        stream.write(xml_str.encode('utf8'))

class ManifestParser( ContentHandler ):

    def __init__(self, manifest=None):
        self._manifest = manifest or Manifest()

    def getManifest( self ):
        return self._manifest

    def startElement( self, name, attrs ):
        if name == u'manifest':
            self._manifest.contenttype = attrs.get('contenttype', '')
            self._manifest.uid = attrs.get('uid', '')
        elif name == u'entry':
            self._manifest.manifest.append({
                       'type':attrs.get('type', ''),
                       'name':attrs.get('name', ''),
                       'filename':attrs.get('filename',''),
                       'mimetype':attrs.get('mimetype', ''),
                       'fullpath':attrs.get('fullpath', ''),
                       })

if __name__ == '__main__':
    mi = Manifest()
    mi.load(open('sample-manifest.xml').read())
    print 'contenttype:', mi.contenttype
    print 'uid: ', mi.uid
    print 'files:', mi.manifest

    from StringIO import StringIO
    stream = StringIO()
    mi.write2xml(stream)
    # print stream.getvalue()

