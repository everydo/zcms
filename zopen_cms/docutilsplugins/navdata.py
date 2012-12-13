# -*- encoding: utf-8 -*-

from pyramid.url import resource_url

from zopen_cms.models import Folder, Document, File, Image

class NavTreeData(object):
    """ 一个适配器，获得根据当前上下文对象显示导航树，所需要的数据 """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def singleBranchTree(self, root=''):
        """ 返回当前节点父节点，以及兄弟节点的清单
        用于显示初始的结构"""
        # get Root And Parents
        current = self.context

        nodes = [current] 
        while current.__parent__ != None:
            current = current.__parent__
            nodes.insert(0,current)

        parent_paths = []
        for node in nodes:
            if isinstance(node, Folder):
                parent_paths.append(node.vpath)
            else:
                break

        if isinstance(root, File):
            return self.obj2Data(root.__parent__, parent_paths)

        return self.obj2Data(root, parent_paths)

    def appendChildren(self, root, parent_paths):
        res = []
        if isinstance(root, Folder):
            for child in root.values(True,True):
                if child.vpath in parent_paths:
                    res.append(self.obj2Data(child, parent_paths))
                else:
                    res.append(self.obj2Data(child))
        return res

    def children(self):
        """ 得到当前节点子节点清单
        用于kss action-server调用 """
        current = self.context
        return [self.obj2Data(child) for child in current.values(True,True)]

    def obj2Data(self, obj, parent_paths=None):
        dc = obj.metadata
        name = obj.__name__
        title = dc.get('title', obj.__name__)
        icon_url = '/static/folder.gif'
        view = '/view.html'

        url = resource_url(obj, self.request)

        if isinstance(obj, Folder):
            view = ''
        else:
            url = url[:-1]

        if isinstance(obj, File):
            icon_url = '/static/file.gif'
        if isinstance(obj, Document):
            icon_url = '/static/document.gif'
            view = ''
        if isinstance(obj, Image):
            icon_url = '/static/image.gif'
        data = {
            'name':name,
            'url':url,
            'view':view,
            'icon':icon_url,
            'title':title,
            'children':[],
            'flag':''
        }
        if not isinstance(obj, Folder):
            data['children']=None
        elif parent_paths is not None:
            data['children'] = self.appendChildren(obj, parent_paths)

        if obj.vpath == self.context.vpath:
            data['flag']='current'
        elif obj.vpath + '/index.rst' == self.context.vpath:
            for child in data['children']:
                if 'index.rst' == data['name']:
                    return data
            data['flag']='current'
        return data
