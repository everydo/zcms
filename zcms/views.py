# -*- encoding: utf-8 -*-

import os
import mimetypes

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render, render_to_response
from pyramid.response import Response

from utils import zcms_template
from models import Folder, Page, Image, File

@view_config(context=Folder)
@zcms_template
def folder_view(context, request):
    if not request.url.endswith('/'):
        response = HTTPFound(location=request.url + '/')
        return response

    for name in ('index.rst', 'index.md'):
        try:
            index = context[name]
        except KeyError:
            continue
        return index, index.render_html(request)

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

    return render(
        'templates/contents_main.pt',
        dict(
            title=title,
            description=description,
            items=items
        )
    )

@view_config(context=Page)
@zcms_template
def document_view(context, request):
    return context.render_html(request)

@view_config(context=File, name="view.html")
@zcms_template
def file_view(context, request):
    return render(
            'templates/file.pt',
            dict(
                title = context.title,
                description = context.metadata.get('description', ''),
                url = context.__name__
            )
        )

@view_config(context=Image, name="view.html")
@zcms_template
def image_view(context, request):
    dc = context.metadata
    title = dc.get('title', context.__name__)
    description = dc.get('description', '')
    url = context.__name__

    return render(
            'templates/image.pt',
            dict(
                title=title,
                description=description,
                url=url,
            )
        )

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
