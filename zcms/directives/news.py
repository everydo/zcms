# -*- coding: utf-8 -*-

# 博客列表指令

"""
目的：动态的生成新闻面板
使用方法::

    .. news:: 
       :path: /edoprojects.com/blogs
       :size: 5

参考： 
http://docutils.sourceforge.net/docs/howto/rst-directives.html

"""
"""
navtree_directive.arguments = (0, 1, 0) 
     three args: required_arguments,optional_arguments,final_argument_whitespace
     .. navtree:: no required_arguments
     :root_depth: one optional_arguments
"""
from docutils import nodes
from pyramid.url import resource_url
from docutils.parsers.rst import directives
from zcms.utils import getDisplayTime

def news_directive(name, arguments, options, content, lineno, content_offset, block_text, state, state_machine):
    context = state.document.settings.context
    request = state.document.settings.request

    parsed = render_news(context, request, options['path'], options.get('size', 5), options.get('class', ''))
    return [nodes.raw('', parsed, format='html')]

news_directive.arguments = (0, 1, 0) 
news_directive.has_content = 1
news_directive.content = 1  
news_directive.options = {'size': int, 'path': str, 'class':str}

directives.register_directive('news', news_directive)

def render_news(context, request, path, size=5, klass='nav nav-list'):
    site = context.get_site()
    container = site.get_obj_by_subpath(path)
    container_url = resource_url(container, request)
    title = container.title

    posts = []
    blog_subpaths = container.get_recent_file_subpaths()

    for subpath in blog_subpaths[:size]:
        obj = container.get_obj_by_subpath(subpath)
        if obj is None: continue

        dc = obj.metadata
        url = resource_url(obj, request)
        if url.endswith('/'): url = url[:-1]
        created = dc.get('modified', dc.get('created', ''))
        posts.append("""<li><a href="%s">%s</a><span>%s</span></li>""" % \
              (url, obj.title, getDisplayTime(created)))

    return '<ul class="%s">%s</ul>' % (klass, ''.join(posts))
