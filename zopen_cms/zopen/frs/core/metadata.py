# -*- encoding:utf-8 -*-
import json
from jsonutils import AwareJSONEncoder,AwareJSONDecoder

class MetadataMixin(object):

    def metadatapath(self, vpath):
        return self.frspath(vpath, 'metadata.json')

    def getMetadata(self, vpath):
        metadatapath = self.metadatapath(vpath)
        if self.exists(metadatapath):
            metadata = json.load(file(self.ospath(metadatapath)),encoding="utf-8",cls=AwareJSONDecoder)
            return metadata
        else:
            return None

    def saveMetadata(self, vpath, metadata_body):
        """ 将一个文件或文件夹的元信息(dict),保存到json中
        """
        metadatapath = self.metadatapath(vpath)

        folderpath = self.dirname(metadatapath)
        if not self.exists(folderpath):
            self.makedirs(folderpath)

        f = self.open(metadatapath, 'w')
        metadata = Metadata(metadata_body)
        json.dump(metadata,f,ensure_ascii=False,indent=4,cls=AwareJSONEncoder)
        f.close()

class Metadata(dict):
    pass

if __name__ == '__main__':
    me = Metadata()
    me.load(file('sample-metadata.json'))
    print 'files:',me.metadata
    print 30*'-','\r','\r'

    from StringIO import StringIO
    stream = StringIO()
    me.write2json(stream)
    print 'stream:',stream.getvalue()
