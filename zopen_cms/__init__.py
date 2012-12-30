# -*- coding: utf-8 -*-
import os
import docutilsplugins

from pyramid.config import Configurator

from zopen_frs import FRS
from zopen_cms.models import Folder

_pyramid_settings = None
_single_root = ''


def main(global_config, sites, **settings):
    global _pyramid_settings
    _pyramid_settings = settings.copy()

    # 根据配置，初始化文件库
    frs = FRS()
    for site_name in os.listdir(sites):
        frs.mount(site_name, os.path.join(sites, site_name))

    def get_root(environ):
        folder = Folder(frs)
        return folder

    config = Configurator(settings=settings, root_factory=get_root)
    config.scan('zopen_cms')
    return config.make_wsgi_app()


