# -*- encoding: utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render

#from z3c.batching.batch import Batch

from models import Page 
from webhelpers import paginate
from utils import getDisplayTime, zcms_template
from datetime import datetime

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
            raw_html = obj.render_html(request)
            converted_html = raw_html.replace(
                'src="img/',
                'src="%s/%s/../img/' % (request.application_url, url)
            )
            created = dc.get('modified', dc.get('created', ''))
            created = datetime.strptime(created, '%Y-%m-%d %H:%M') if created else datetime.now()
            posts.append({
                'title':obj.title,
                'description':dc.get('description', ''),
                'url':subpath,
                'created':getDisplayTime(created),
                'creator':dc.get('creator', ''),
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


@view_config(context=Page, name="blogpost.html")
@zcms_template
def blog_post_view(context, request):
    """ 单独一篇博客 """
    obj = context
    dc = obj.metadata

    result = {}
    result['url'] = obj.__name__
    result['title'] = obj.title
    result['description'] = dc.get('description', '')
    result['created'] = dc.get('modified', dc.get('created', ''))
    result['creator'] = dc.get('creator', '')

    pachs = request.url.split('/')
    img_url =  '/'.join(pachs[0:len(pachs)-2]) + '/img/'
    result['body'] = obj.render_html(request).replace('src="img/', 'src="%s' % img_url)

    idcomments_acct = request.registry.settings.get('idcomments_acct', '')

    title = context.title
    description = dc.get('description', '')
    return render(
        'templates/blogpost_main.pt',
        dict(
            result = result,
            post_created = getDisplayTime(result['created']),
            idcomments_acct = idcomments_acct,
        )
    )

