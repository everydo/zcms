# -*- coding: utf-8 -*-
import os
import directives 

from pyramid.config import Configurator

from frs import FRS
from models import Folder

def main(global_config, sites, **settings):

    # 根据配置，初始化文件库
    frs = FRS()
    for site_name in os.listdir(sites):
        frs.mount(site_name, os.path.join(sites, site_name))

    def get_root(environ):
        folder = Folder(frs)
        return folder

    config = Configurator(settings=settings, root_factory=get_root)
    config.scan('zcms')
    return config.make_wsgi_app()


