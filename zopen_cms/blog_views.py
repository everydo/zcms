# -*- encoding: utf-8 -*-

from pyramid.view import view_config
from pyramid.url import resource_url
from pyramid.response import Response
from pyramid.renderers import render

#from z3c.batching.batch import Batch

from models import Document
from views import render_tabs, render_cols
from batch_views import batch_view as render_batch
from utils import getDisplayTime, get_site, render_html

def blog_view(context, request, size=5):
    batch_start = request.params.get('b_start', '0')
    # XXX hack, 很奇怪会附加一个/
    if batch_start.endswith('/'):
        batch_start = batch_start[:-1]
    batch_start = int(batch_start)
    posts = []
    #blog_subpaths = Batch(context.get_recent_file_subpaths(), start=batch_start, size=size)
    blog_subpaths = context.get_recent_file_subpaths()

    for subpath in blog_subpaths:
        obj = context.get_obj_by_subpath(subpath)
        if obj is not None:
            url = '/'.join(obj.vpath.split('/')[2:])
            dc = obj.metadata.get('dublin', {})
            raw_html = render_html(obj, request)
            converted_html = raw_html.replace(
                'src="img/',
                'src="%s/%s/../img/' % (request.application_url, url)
            )
            posts.append({
                'title':dc.get('title', obj.__name__),
                'description':dc.get('description', ''),
                'url':subpath,
                'created':getDisplayTime(dc.get('modified', dc.get('created', ''))),
                'creator':dc.get('creators', [])[0],
                'body':converted_html,
            })

    batch = '' # render_batch(blog_subpaths, request)
    return render(
        'templates/bloglist.pt',
        dict(
            result = posts,
            batch = batch,
        )
    )

def news_portlet(context, request, path, size=5):
    site = get_site(context)
    container = site.get_obj_by_subpath(path)
    container_url = resource_url(container, request)
    title = container.title

    posts = []
    blog_subpaths = container.get_recent_file_subpaths()

    for subpath in blog_subpaths[:size]:
        obj = container.get_obj_by_subpath(subpath)
        if obj is not None:
            dc = obj.metadata.get('dublin', {})
            url = resource_url(obj, request)
            if url.endswith('/'): url = url[:-1]
            posts.append({
                'title':dc.get('title', obj.__name__),
                'description':dc.get('description', ''),
                'url':url,
                'created':getDisplayTime(dc.get('modified', dc.get('created', ''))),
                'creator':dc.get('creators', [])[0],
            })

    return render(
        'templates/portlet_news.pt', 
        dict(
            title = title, 
            result = posts,
            container_url = container_url
        )
    )

@view_config(context=Document, name="blogpost.html")
def blog_post_view(context, request):
    """ 单独一篇博客 """
    obj = context
    dc = obj.metadata.get('dublin',{})

    result = {}
    result['url'] = obj.__name__
    result['title'] = dc.get('title', obj.__name__)
    result['description'] = dc.get('description', '')
    result['created'] = dc.get('modified', dc.get('created', ''))
    result['creator'] = dc.get('creators', [])[0]

    pachs = request.url.split('/')
    img_url =  '/'.join(pachs[0:len(pachs)-2]) + '/img/'
    result['body'] = render_html(obj, request).replace('src="img/', 'src="%s' % img_url)

    tabs = render_tabs(context,request)
    cols = render_cols(context, request)
    idcomments_acct = request.registry.settings.get('idcomments_acct', '')

    title = dc.get('title', context.__name__)
    description = dc.get('description', '')
    content = render(
        'templates/blogpost_main.pt',
        dict(
            result = result,
            post_created = getDisplayTime(result['created']),
            idcomments_acct = idcomments_acct,
        )
    )

    kw = dict(
        title = title,
        head = '<title>%s</title>' % title,
        nav = tabs,
        left_col = cols.get('left', ''),
        right_col = cols.get('right', ''),
        content = content,
        description = description
    )
    request.environ['zopen_cms.kw'] = kw

    return Response(headerlist=[('Content-type','text/html')]) 

    # return render_to_response(
    #     'templates/blogpost.pt',
    #     dict(
    #         title = dc.get('title', context.__name__),
    #         result = result,
    #         tabs = tabs,
    #         cols = cols,
    #         post_created = getDisplayTime(result['created']),
    #         idcomments_acct = idcomments_acct,
    #     )
    # )
