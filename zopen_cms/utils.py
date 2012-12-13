# -*- encoding: utf-8 -*-

from datetime import datetime
from docutils.core import publish_parts
from docutils.writers.html4css1 import Writer

def getDisplayTime(input_time, show_mode='localdate'):
    """ 人性化的时间显示: (支持时区转换)

    time 是datetime类型，或者timestampe的服点数，
    最后的show_mode是如下:

    - localdate: 直接转换为本地时间显示，到天
    - localdatetime: 直接转换为本地时间显示，到 年月日时分
    - localtime: 直接转换为本地时间显示，到 时分
    - deadline: 期限，和当前时间的比较天数差别，这个时候返回2个值的 ('late', '12天前')
    - humandate: 人可阅读的天，今天、明天、后天、昨天、前天，或者具体年月日 ('today', '今天')
    """
    if not input_time:
        return ''
    
    today = datetime.now()
    time_date = datetime(input_time.year, input_time.month, input_time.day)
    year, month, day = today.year, today.month, today.day
    today_start = datetime(year, month, day)

    to_date = today_start - time_date

    # 期限任务的期限
    if show_mode == 'localdate':
        return input_time.strftime('%Y-%m-%d')
    elif show_mode == 'localdatetime':
        return input_time.strftime('%Y-%m-%d %H:%M')
    elif show_mode == 'localtime':
        return input_time.strftime('%H:%M')
    elif show_mode == 'deadline':
        if to_date == 0:
            return ('Today', '今天')
        elif to_date < 0:
            if to_date == -1:
                return (None, '明天')
            elif to_date == -2:
                return (None, '后天')
            else:
                return (None, str(int(-to_date))+'天')
        elif to_date > 0:
            if to_date == 1:
                return ('late', '昨天')
            elif to_date == 2:
                return ('late', '前天')
            else:
                return ('late', str(int(to_date))+'天前')
    elif show_mode == 'humandate':
        if to_date == 0:
            return ('Today', '今天')
        elif to_date < 0:
            if to_date == -1:
                return (None, '明天')
            elif to_date == -2:
                return (None, '后天')
            else:
                return (None, input_time.strftime('%Y-%m-%d'))
        elif to_date > 0:
            if to_date == 1:
                return ('late', '昨天')
            elif to_date == 2:
                return ('late', '前天')
            else:
                return ('late', input_time.strftime('%Y-%m-%d'))

def get_sub_time_paths(folder, root_vpath):
    """ 迭代查找整个子目录，找出所有的子文档的路径 """
    from models import Folder, Document

    result = []
    for obj in folder.values(True, False):
        dc = obj.metadata
        if isinstance(obj, Folder):
            result.extend(get_sub_time_paths(obj, root_vpath))
        elif isinstance(obj, Document):
            result.append((
                dc.get('modified', 
                dc.get('created', '')),
                obj.vpath.replace(root_vpath + '/', ''),
            ))
    return result

def rst2html(rst, path, context, request):
    settings = {
        'halt_level':6,
        'input_encoding':'UTF-8',
        'output_encoding':'UTF-8',
        'initial_header_level':2,
        'file_insertion_enabled':1,
        'raw_enabled':1,
        'writer_name':'html',
        'language_code':'zh_cn',
        'context':context,
        'request':request
    }

    # TODO(Prim): rst文本里面有border="1"?
    # 表格生成的时候，会出现一个border=1，需要去除
    rst = rst.replace('border="1"', '')

    return publish_parts(
        rst,
        source_path = path,
        writer = Writer(),
        settings_overrides = settings
    )['html_body']

def render_html(frs_file, request):
    data = frs_file.data

    lstrip_data = data.lstrip()
    # windows会自动增加utf8的标识字
    if lstrip_data[0:3]== '\xef\xbb\xbf':
        lstrip_data = lstrip_data[3:]

    # 判断文件内容是否为html
    # 文件内容不是html时，认为内容为rst文本
    if lstrip_data and lstrip_data[0] == '<':
        return data

    # 不显示的标题区域，标题在zpt里面独立处理了
    if lstrip_data.startswith('======'):
        splitted_data = lstrip_data.split('\n', 3)
        data = splitted_data[-1]
        # title = splitted_data[1]

    ospath = frs_file.ospath
    return rst2html(data, str(ospath), frs_file, request)

def get_site(context):
    while context.vpath.find('/', 1) != -1:
        context = context.__parent__
    return context
