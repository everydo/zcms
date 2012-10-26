# -*- encoding:utf-8 -*-
import json
import os

#定义常见的文件夹类型
Folder_Types = ['Folder',
               'Blog',
               'BlogFolder',
               'HelpCenter',
               'HelpCenterFAQFolder',
               'HelpCenterHowToFolder',
               'HelpCenterTutorialFolder',
               'HelpCenterTutorial',
               'COREBlog2',
               'COREBlogCategory',
               'COREBlogCategoryFolder',
                ]

def export(self):
    """ 程序入口"""
    info = getMetadata(self)
    dump_root = os.path.join(os.environ['INSTANCE_HOME'], 'var', 'frsdump')
    if not os.path.exists(dump_root):
        os.makedirs(dump_root)
    os.chdir(dump_root)
    try:
        frsexport(info)
    except Exception,e:
        return e
    return "export success!"

def getMetadata(self):
    """
    导出格式为:
    [{'title':title,'creator':creator,'contenttype':contenttype,'id':id,'modified':modified},{}]
    """
    info = []
    for obj in self.contentValues():
        metadata = {}
        #id为文件名
        metadata['id'] = unicode(obj.getId())
        metadata['title'] = unicode(obj.Title()) or unicode(obj.getId())
        metadata['creator'] = unicode(obj.Creator())
        metadata['description'] = unicode(obj.Description())
        metadata['modified'] = obj.modified().strftime("%Y-%m-%d %H:%M:%S")
        metadata['contenttype']= unicode(obj.getPortalTypeName())

        if metadata['contenttype'] in Folder_Types:
            #各种文件夹类型保存为文件夹
            metadata['contenttype'] = 'Folder'
            subobject = getMetadata(obj)
            metadata['subobject'] = subobject
            metadata['keys'] = [ (key == obj.getDefaultPage() and 'index.rst' or \
                    key) for key in obj.contentIds()]
            metadata['hidden_keys'] = [(item.getId() == obj.getDefaultPage() and 'index.rst'or item.getId())\
               for item in obj.contentValues() if (hasattr(item,"getExcludeFromNav") and item.getExcludeFromNav())]
        else:
            metadata['mimetype'] = unicode(obj.getContentType())

            if metadata['contenttype'] == 'Image':
                if isinstance(obj.getRawImage(),str):
                    metadata['data'] = obj.getRawImage()
                else:
                    metadata['data'] = str(obj.getRawImage().data)

            elif metadata['contenttype'] == 'Document':
                metadata['data'] = unicode(obj.getRawText())
                if self.getDefaultPage() == obj.getId():
                  metadata['id'] = 'index.rst'

            elif metadata['contenttype'] == 'File':
                metadata['data'] = str(obj.getRawFile().data)

            elif metadata['contenttype'] == 'News Item':
                #新闻保存为文本
                metadata['contenttype'] = 'Document'
                metadata['data'] = unicode(obj.CookedBody())

            elif metadata['contenttype'] == 'BlogEntry':
                #博客日志保存为文本
                metadata['contenttype'] = 'Document'
                metadata['data'] = unicode(obj.getBody())

            elif metadata['contenttype'] == 'COREBlogEntry':
                #博客日志保存为文本
                metadata['contenttype'] = 'Document'
                metadata['data'] = unicode(obj.getBody())
                metadata['modified'] = unicode(obj.Date())

            elif metadata['contenttype'] == 'HelpCenterFAQ':
                #FAQ保存为文本
                metadata['contenttype'] = 'Document'
                metadata['data'] = unicode(obj.getAnswer())

            elif metadata['contenttype'] == 'HelpCenterHowTo':
                #HowTo保存为文本
                metadata['contenttype'] = 'Document'
                metadata['data'] = unicode(obj.getBody())

            elif metadata['contenttype'] == 'HelpCenterTutorialPage':
                #Tutorial保存为文本
                metadata['contenttype'] = 'Document'
                metadata['data'] = unicode(obj.getBody())

            else:
                continue

        info.append(metadata)

    return info


def frsexport(all_files):
    """ 导出到文件系统中 """

    #先导出当前层次的文件
    for newfile in all_files:
        if newfile['contenttype'] not in Folder_Types:
            mkfile(newfile)
    #后从当前层次的文件夹开始迭代导出
    for newfolder in all_files:
        if newfolder['contenttype'] in Folder_Types:
            oldpath = os.getcwd()
            dirpath = mkfile(newfolder,"folder")
            os.chdir(dirpath)
            frsexport(newfolder['subobject'])
            os.chdir(oldpath)

def mkfile(newfile,file_type="file"):
    """ 导出文件和文件夹
        file_type : file,folder
    """
    #构造元数据
    metadata = {}
    metadata['main'] = {}
    metadata['dublin'] = {}
    metadata['main']['id'] = newfile['id']
    metadata['main']['contenttype'] = newfile['contenttype']
    metadata['dublin']['title'] = newfile['title']
    metadata['dublin']['description'] = newfile['description']
    metadata['dublin']['creators'] = (newfile['creator'],)
    metadata['dublin']['modified'] = newfile['modified']
    # 写入元数据
    frspath = os.path.join(os.getcwd(),'.frs',newfile['id'])
    if not os.path.exists(frspath):
        os.makedirs(frspath)
    metadatapath = os.path.join(frspath,'metadata.json')
    f = file(metadatapath,'wb')
    json.dump(metadata,f,ensure_ascii=False,indent=4)
    f.close()
    # 在文件系统中生成文件或文件夹,如果是文件夹返回其路径
    if file_type=='folder':
        if not os.path.exists(newfile['id']):
            os.mkdir(newfile['id'])
        dirpath = os.path.join(os.getcwd(),newfile['id'])
        return dirpath
    else:
        out = file(newfile['id'],'w')
        out.write(newfile['data'])
        out.close()

