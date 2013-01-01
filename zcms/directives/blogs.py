# -*- coding: utf-8 -*-

# 博客列表指令

"""
目的：动态的生成博客列表html
使用方法::

    .. blogs:: asdfasdfasd
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
from zcms.blog_views import blog_view

def blogs_directive(name, arguments, options, content, lineno,
                    content_offset, block_text, state, state_machine):
    context = state.document.settings.context
    request = state.document.settings.request

    parsed = blog_view(context.__parent__, request, options.get('size', 5))
    return [nodes.raw('', parsed, format='html')]

blogs_directive.arguments = (0, 1, 0) 
blogs_directive.has_content = 1
blogs_directive.content = 1  
blogs_directive.options = {'size': int}

directives.register_directive('blogs', blogs_directive)

