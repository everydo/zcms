# -*- coding: utf-8 -*- 
import os
import docutilsplugins

from string import Template
from pyramid.config import Configurator

from zopen.frs.core import FRS
from zopen_cms.models import Folder

_templates_cache = {}
_pyramid_settings = None
_single_root = ''

def main(global_config, roots, **settings):
    global _pyramid_settings 
    _pyramid_settings = settings.copy()

    # 根据配置，初始化文件库
    frs = FRS()
    roots = roots.split('\n')
    for root in roots:
        root = root.strip()
        mount_name = os.path.basename(root) or os.path.basename(root[:-1])
        frs.mount(mount_name, root)

    def get_root(environ):
        folder = Folder(frs)

        # DEBUG模式下只显示第一个站点
        if _pyramid_settings['single_root'] == 'true': 
            root = roots[0]
            mount_name = os.path.basename(root) or os.path.basename(root[:-1])
            site = folder[mount_name]

            global _single_root
            _single_root = site.__name__
            site.__name__, site.__parent__ = '', None
            return site

        return folder
 
    config = Configurator(settings=settings, root_factory=get_root)
    config.scan('zopen_cms')
    return config.make_wsgi_app()

class Theme(object):
    """WSGI中间件, 用于将pyramid response的内容渲染到theme中"""

    def __init__(self, app, global_config, theme, **settings):
        self.app = app
        self.theme = theme

    def __call__(self, environ, start_response):

        # 线上运行，多站点支持
        global _pyramid_settings
        if _pyramid_settings['single_root'] != 'true':
            path_info = environ['PATH_INFO'].split('/', 2)
            site = path_info[1]
            environ['HTTP_X_VHM_ROOT'] = '/' + site
            environ['PATH_INFO'] = '/%s' % path_info[2]

        def _(status, headers, exc_info=None):
            pass
        self.app(environ, _)

        if 'zopen_cms.kw' in environ:
            site = _single_root or path_info[1]
            theme = os.path.join(self.theme, site, 'index.html')
            kw = environ['zopen_cms.kw']
            
            # NOTE(Prim): 根据debug_templates判断是否使用全局变量做缓存
            if _pyramid_settings['debug_templates'] == 'true':
                template = Template(open(theme).read())
            else:
                global _templates_cache
                if theme in _templates_cache:
                    template = _templates_cache[theme]
                else:
                    template = Template(open(theme).read())
                    _templates_cache[theme] = template

            output = str(template.substitute(kw))
            headers = [
                ('Content-length', str(len(output))),
                ('Content-type', 'text/html; charset=UTF-8')
            ]
            start_response('200 OK', headers)
            return output

        return self.app(environ, start_response)
