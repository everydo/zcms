# -*- encoding: utf-8 -*-

import os
import mimetypes

from pyramid.view import view_config
from pyramid.url import resource_url
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render, render_to_response

from utils import rst2html, get_site, render_html
from models import Folder, Document, Image, File


def render_tabs(context, request):
    site = get_site(context)
    if site is None:
        return ''

    html_list = []
    for tab in site.values(True, True):
        class_str = 'plain'
        if context.vpath.startswith(tab.vpath):
            class_str = "selected"

        tab_url = resource_url(tab, request)  # hack
        if tab_url.endswith('.rst/'):
            tab_url = tab_url[:-1]

        html_list.append(
            '<li id="nav-%s" class="%s"><a href="%s">%s</a></li>'
            % (tab.__name__, class_str, tab_url, tab.title)
        )

    html = '<ul id="portal-globalnav">%s</ul>' % ''.join(html_list)
    return html.decode('utf-8')


def rst_col_path(name, context):
    # 往上找左右列
    if context.__name__ == '':
        return '', ''
    source_path = str(context.ospath)
    if isinstance(context, Folder):
        source_path = os.path.join(source_path, 'asf.rst')
    dc_main = context.metadata
    col = dc_main.get(name, '')
    if col != '':
        return col, source_path
    if context.__parent__ is None:
        return col, source_path
    return rst_col_path(name, context.__parent__)


def render_cols(context, request):
    html_left = ''
    html_right = ''
    right_col_rst, right_col_path = rst_col_path('right_col', context)
    left_col_rst, left_col_path = rst_col_path('left_col', context)
    center_col_rst, center_col_path = rst_col_path('center_col', context)

    if left_col_rst == '':
        html_left = ''
    else:
        cvt_html = rst2html(left_col_rst, left_col_path, context, request)
        if cvt_html.startswith('<td') or cvt_html.lstrip().startswith('<td'):
            html_left = cvt_html
        else:
            html_left = """<td id="portal-column-one">
                <div class="visualPadding">%s</div></td>
                """ % rst2html(left_col_rst, left_col_path, context, request)

    if right_col_rst == '':
        html_right = ''
    else:
        cvt_html = rst2html(right_col_rst, right_col_path, context, request)
        if cvt_html.startswith('<td') or cvt_html.lstrip().startswith('<td'):
            html_right = cvt_html
        else:
            html_right = """<td id="portal-column-two">
                <div class="visualPadding">%s</div></td>
                """ % rst2html(right_col_rst, right_col_path, context, request)

    if center_col_rst == '':
        html_center = ''
    else:
        cvt_html = rst2html(center_col_rst, center_col_path, context, request)
        html_center = '<div>%s</div>' % rst2html(
            center_col_rst, center_col_path, context, request)

    html_cols = {
        'left': html_left,
        'right': html_right,
        'center': html_center
    }
    return html_cols

# NOTE(Prim): 通用组件
#   - head
#   - content
#   - left/right_col
#   - nav


@view_config(context=Folder)
def folder_view(context, request):
    if not request.url.endswith('/'):
        response = HTTPFound(location=request.url + '/')
        return response

    defaults = ('index.html', 'index.rst')
    for name in defaults:
        try:
            index = context[name]
        except KeyError:
            continue
        return document_view(index, request)

    items = []
    for obj in context.values(True, True):
        dc = obj.metadata
        if hasattr(obj, '__getitem__'):
            url = obj.__name__ + '/'
        else:
            url = obj.__name__
        items.append({
            'name': obj.__name__,
            'title': dc.get('title', '') or obj.__name__,
            'url': url,
            'description': dc.get('description', '')
        })

    dc = context.metadata

    if context.vpath != '/':
        nav = render_tabs(context, request)
    else:
        nav = ''
    html_cols = render_cols(context, request)
    title = dc.get('title', context.__name__)
    description = dc.get('description', '')

    content = render(
        'templates/contents_main.pt',
        dict(
            title=title,
            description=description,
            items=items
        )
    )

    kw = dict(
        title=title,
        items=items,

        head='<title>%s</title>' % title,
        nav=nav,
        left_col=html_cols.get('left', ''),
        right_col=html_cols.get('right', ''),
        content=content,
        description=description
    )

    if context.vpath != '/':
        request.environ['zopen_cms.kw'] = kw

    if request.registry.settings.get('debug_templates', ''):
        return render_to_response('templates/contents.pt', kw)
    return Response(headerlist=[('Content-type', 'text/html')])


@view_config(context=Document)
def document_view(context, request):
    html = render_html(context, request)
    html_cols = render_cols(context, request)
    site = get_site(context)
    site_title = site.title
    dc = context.metadata
    tabs = render_tabs(context, request)
    description = dc.get('description', '')
    doc_title = dc.get('title', '')
    if not isinstance(doc_title, (str, unicode)):
        doc_title = ''
    if doc_title:
        site_title = doc_title + ' - ' + site_title

    content = render(
        'templates/document_main.pt',
        dict(
            title=doc_title,
            description=description,
            html=html,
            html_cols=html_cols
        )
    )

    kw = dict(
        site_title=site_title,

        head='<title>%s</title>' % site_title,
        nav=tabs,
        left_col=html_cols.get('left', ''),
        right_col=html_cols.get('right', ''),
        content=content,
        description=description
    )
    request.environ['zopen_cms.kw'] = kw

    if request.registry.settings.get('debug_templates', ''):
        return render_to_response('templates/document.pt', kw)
    return Response(headerlist=[('Content-type', 'text/html')])


@view_config(context=File, name="view.html")
def file_view(context, request):
    dc = context.metadata
    tabs = render_tabs(context, request)
    title = dc.get('title', context.__name__)
    description = dc.get('description', '')
    url = context.__name__

    kw = dict(
        title=title,
        description=description,
        url=url,
        tabs=tabs,
        content=render(
            'templates/file.pt',
            dict(
                title=title,
                description=description,
                url=url,
                tabs=tabs
            )
        )
    )
    request.environ['zopen_cms.kw'] = kw
    if request.registry.settings.get('debug_templates', ''):
        return render_to_response('templates/file.pt', kw)
    return Response(headerlist=[('Content-type', 'text/html')])


@view_config(context=Image, name="view.html")
def image_view(context, request):
    dc = context.metadata
    tabs = render_tabs(context, request)
    title = dc.get('title', context.__name__)
    description = dc.get('description', '')
    url = context.__name__

    kw = dict(
        title=title,
        description=description,
        url=url,
        tabs=tabs,
        content=render(
            'templates/image.pt',
            dict(
                title=title,
                description=description,
                url=url,
                tabs=tabs
            )
        )
    )
    request.environ['zopen_cms.kw'] = kw

    if request.registry.settings.get('debug_templates', ''):
        return render_to_response('templates/image.pt', kw)
    return Response(headerlist=[('Content-type', 'text/html')])


@view_config(context=File)
def download_view(context, request):
    response = Response(context.data)
    filename = context.frs.basename(context.vpath)
    mt, encoding = mimetypes.guess_type(filename)
    if isinstance(context, Document):
        response.content_type = 'text/html'         # mt or 'text/plain'
    else:
        response.content_type = mt or 'text/plain'
    return response
