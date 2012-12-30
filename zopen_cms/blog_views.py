# -*- encoding: utf-8 -*-

from pyramid.view import view_config
from pyramid.url import resource_url
from pyramid.response import Response
from pyramid.renderers import render

#from z3c.batching.batch import Batch

from models import Document
from webhelpers import paginate
from utils import getDisplayTime, get_site, render_html, render_content

def blog_view(context, request, size=5):
    current_page = request.params.get('page', '0')
    # XXX hack, 很奇怪会附加一个/
    if current_page.endswith('/'):
        current_page = current_page[:-1]
    current_page = int(current_page)
    page_url = paginate.PageURL_WebOb(request)
    blog_subpaths = context.get_recent_file_subpaths()
    blog_page = paginate.Page(blog_subpaths, current_page, items_per_page=size, url=page_url)

    posts = []
    for subpath in blog_page:
        obj = context.get_obj_by_subpath(subpath)
        if obj is not None:
            url = '/'.join(obj.vpath.split('/')[2:])
            dc = obj.metadata
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
                'creator':dc.get('creators', [''])[0],
                'body':converted_html,
            })

    batch = blog_page.pager()
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
        if obj is not None: continue

        dc = obj.metadata
        url = resource_url(obj, request)
        if url.endswith('/'): url = url[:-1]
        created = dc.get('modified', dc.get('created', ''))
        posts.append("""<li><a href="%s">%s</a><span>%s</span></li>""" % \
              (url, dc.get('title', obj.__name__), getDisplayTime(created)))

    return ''.join(posts)

@view_config(context=Document, name="blogpost.html")
def blog_post_view(context, request):
    """ 单独一篇博客 """
    obj = context
    dc = obj.metadata

    result = {}
    result['url'] = obj.__name__
    result['title'] = dc.get('title', obj.__name__)
    result['description'] = dc.get('description', '')
    result['created'] = dc.get('modified', dc.get('created', ''))
    result['creator'] = dc.get('creators', [])[0]

    pachs = request.url.split('/')
    img_url =  '/'.join(pachs[0:len(pachs)-2]) + '/img/'
    result['body'] = render_html(obj, request).replace('src="img/', 'src="%s' % img_url)

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

    return render_content(context, request, content)
