# -*- coding: utf-8 -*-

# 导航树指令

"""
目的：动态的生成导航树html
使用方法::

    .. navtree:: asdfasdfasd
       :root_depth: 1
       :class: nav nav-pills nav-stacked

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
from string import Template
from pyramid.url import resource_url
from zcms.models import Folder, File, Image

nav_root_template = Template(r""" <ul class="${ul_class}"> ${nav_items} </ul> """)

nav_item_template = Template(r"""
<li class="${class_str}"> <a href="${node_url}"> ${node_title} </a> </li>""")

def navtree_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    context = state.document.settings.context
    request = state.document.settings.request

    parsed = nav_tree(context, request, options.get('root_depth', 1), options.get('class', 'nav nav-list'))
    return [nodes.raw('', parsed, format='html')]

navtree_directive.arguments = (0, 1, 0)
navtree_directive.has_content = 1
navtree_directive.content = 1 
navtree_directive.options = {'root_depth': int, 'class':str}

directives.register_directive('navtree', navtree_directive)

# 生成navtree
def nav_tree(context, request, root_depth, klass):
    """render navtree structure, root_depth from root"""
    # get the root accoding to root_depth
    if isinstance(context, Folder):
        parents = [context]
    else:
        parents = []
    current = context.__parent__
    while current.__parent__:
        parents.insert(0, current)
        current = current.__parent__

    # 超界
    if len(parents) < root_depth + 1:
        return ''

    root = parents[root_depth]
    nodes = []
    parent_paths = [obj.vpath for obj in parents]
    for obj in root.values(True, True):
        is_active = obj.vpath in parent_paths or obj.vpath == context.vpath
        nodes.append(
           nav_item_template.substitute(
               class_str = 'active' if is_active else '',
               node_url = resource_url(obj, request),
               node_title = obj.title,
           ))

    nav_items = ''.join(nodes)
    return nav_root_template.substitute(ul_class=klass, nav_items=nav_items)

