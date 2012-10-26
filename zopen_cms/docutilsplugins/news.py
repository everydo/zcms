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
from docutils.parsers.rst import directives
from zopen_cms.blog_views import news_portlet

def news_directive(name, arguments, options, content, lineno, content_offset, block_text, state, state_machine):
    context = state.document.settings.context
    request = state.document.settings.request

    parsed = news_portlet(context, request, options['path'], options.get('size', 5))
    return [nodes.raw('', parsed, format='html')]

news_directive.arguments = (0, 1, 0) 
news_directive.has_content = 1
news_directive.content = 1  
news_directive.options = {'size': int, 'path': str}

directives.register_directive('news', news_directive)

