# -*- coding: utf-8 -*-

# 导航树指令

"""
目的：动态的生成导航树html
使用方法::

    .. navtree:: asdfasdfasd
       :root_depth: 2
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
from navdata import NavTreeData
from zopen_cms.models import Folder
from string import Template

nav_root_template = Template(r""" <ul class="${ul_class}"> ${nav_items} </ul> """)

nav_item_template = Template(r"""
<li class="${class_str}"> <a href="${node_url}"> ${node_title} </a> ${children_str} </li>""")

def navtree_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    context = state.document.settings.context
    request = state.document.settings.request

    parsed = nav_tree(context, request, options.get('root_depth', 2), options.get('class', 'nav nav-list'))
    return [nodes.raw('', parsed, format='html')]

navtree_directive.arguments = (0, 1, 0)
navtree_directive.has_content = 1
navtree_directive.content = 1 
navtree_directive.options = {'root_depth': int, 'class':str}

directives.register_directive('navtree', navtree_directive)

# 生成navtree
def nav_tree(context, request, root_depth, klass):
    """render navtree structure, root_depth from root"""
    navtree = NavTreeData(context,request)
    if navtree == None:
        return
    # get the root accoding to root_depth
    con = context
    parents = []
    while con.__parent__ != None:
        parents.insert(0,con.__parent__)
        con = con.__parent__

    if isinstance(context, Folder):
        parents.append(context)
    # 超界
    actual_depth = root_depth + 1
    while actual_depth > len(parents):
        actual_depth -= 1
    root = navtree.singleBranchTree(parents[actual_depth-1])
    # 可能不需要显示
    if root == None:
        return

    root_url = root.get('url')
    root_title = root.get('title')
    tree = root.get('children',[])
    items = []
    dept = 0
    for node in tree:
        items.append(renderNode(node,dept))
        dept += 1
    nav_items = ''.join(items)
    return nav_root_template.substitute(tree=tree,\
		             ul_class=klass,
                             root_url=root_url,\
                             root_title=root_title,\
                             nav_items=nav_items)

def renderNode(node, dept=0):
    """Supplies node for nav_tree"""
    # 初始化
    children_str = ''

    if node.get('flag', '')=='current':
        class_str = " active"
    else:
        class_str = ''

    if node['children'] != None and node['children']!=[]:
        class_str += ' loaded expanded'
        children_str += """<ul class="nav nav-list">""" 
        # 最多显示30个节点
        for child_node in node['children'][:30]:
            children_str += renderNode(child_node, dept+1)
        children_str += '</ul>'
    elif not node['name'].endswith('.rst'):
        class_str += ' notloaded collapsed'

    return nav_item_template.substitute(
        class_str = class_str,
        node_url = node['url'],
        node_title = node['title'],
        children_str = children_str
    )
