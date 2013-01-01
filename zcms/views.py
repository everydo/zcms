# -*- encoding: utf-8 -*-

import os
import mimetypes

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render, render_to_response
from pyramid.response import Response

from utils import render_html, render_content
from models import Folder, Page, Image, File

@view_config(context=Folder)
def folder_view(context, request):
    if not request.url.endswith('/'):
        response = HTTPFound(location=request.url + '/')
        return response

    defaults = ('index.rst', 'index.md')
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

    return render_content(context, request, content)

@view_config(context=Page)
def document_view(context, request):
    html = render_html(context, request)
    return render_content(context, request, html)

@view_config(context=File, name="view.html")
def file_view(context, request):
    content = render(
            'templates/file.pt',
            dict(
                title = context.title,
                description = context.metadata.get('description', ''),
                url = context.__name__
            )
        )
    return render_content(context, request, content)

@view_config(context=Image, name="view.html")
def image_view(context, request):
    dc = context.metadata
    title = dc.get('title', context.__name__)
    description = dc.get('description', '')
    url = context.__name__

    content=render(
            'templates/image.pt',
            dict(
                title=title,
                description=description,
                url=url,
            )
        )
    return render_content(context, request, content)

@view_config(context=File)
def download_view(context, request):
    response = Response(context.data)
    filename = context.frs.basename(context.vpath)
    mt, encoding = mimetypes.guess_type(filename)
    if isinstance(context, Page):
        response.content_type = 'text/html'         # mt or 'text/plain'
    else:
        response.content_type = mt or 'text/plain'
    return response
