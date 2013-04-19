# -*- encoding: utf-8 -*-

__docformat__ = 'restructuredtext'
import yaml
import time
import tempfile
import os.path
import stat
import posixpath
from pyramid.threadlocal import get_current_registry
import markdown
import fnmatch
from utils import rst2html

def get_sub_time_paths(folder, root_vpath):
    """ 迭代查找整个子目录，找出所有的子文档的路径 """

    result = []
    for obj in folder.values(True, False):
        dc = obj.metadata
        if isinstance(obj, Folder):
            result.extend(get_sub_time_paths(obj, root_vpath))
        elif isinstance(obj, Page):
            result.append((
                dc.get('modified', 
                dc.get('created', '')),
                obj.vpath.replace(root_vpath + '/', ''),
            ))
    return result

class FRSAsset(object):

    __parent__ = None
    __name__ = ''

    def __init__(self, frs, vpath=u'/'):
        self.frs = frs
        self.vpath = vpath
        self._md = None

    @property
    def ospath(self):
        return self.frs.ospath(self.vpath)


    @property
    def title(self):
        title = self.metadata.get('title', '')
	if title: return title
	return self.__name__.split('.', 1)[0].replace('-', ' ')

    def get_site(self):
        """ 得到所属的站点 """
        context = self
        while context.vpath.find('/', 1) != -1:
            context = context.__parent__
        return context

    def _get_slot_info(self, name):
        # 往上找左右列
        if self.__name__ == '':
             return '', ''
        source_path = str(self.ospath)
        if isinstance(self, Folder):
            rst_path = os.path.join(source_path, '_' + name + '.rst')
        else:
            rst_path = os.path.join(os.path.dirname(source_path), '_' + name + '_' + self.__name__)

        if os.path.exists(rst_path):
            col = open(rst_path).read()
            return col, source_path

        if self.__parent__ is None:
            return '', source_path
        return self.__parent__._get_slot_info(name)

    def render_slots(self, name, request):
        """ name can be: left, right, upper """
        rst_content, rst_path = self._get_slot_info(name)
        if rst_content != '':
            return rst2html(rst_content, rst_path, self, request)
        else:
            return ''

class Folder(FRSAsset):

    @property
    def metadata(self):
        metadatapath = self.frs.joinpath(self.vpath, '_config.yaml')
        try:
            return yaml.load(self.frs.open(metadatapath))
        except KeyError:
            return {}
        except IOError:
            return {}

    def _filter(self, key):
        """Subclasses may overwrite this method.

        Filter possible assets.
        """
        return (not key.startswith('.'))

    def _get(self, key):
        key = key.encode('utf-8')  # key is unicode by default

        if not self._filter(key):
            raise KeyError(key)

        try:
            path = self.frs.joinpath(self.vpath, key)
            st = self.frs.stat(path)
        except OSError:
            raise KeyError(key)

        if stat.S_ISDIR(st.st_mode):
            obj = Folder(self.frs, path)
        elif stat.S_ISREG(st.st_mode):
            ext = posixpath.splitext(path)[1].lower()
            if ext in ['.gif', '.bmp', '.jpg', '.jpeg', '.png']:
                obj = Image(self.frs, path)
            elif ext in ['.html', '.htm', '.rst', '.md']:
                obj = Page(self.frs, path)
            else:
                obj = File(self.frs, path)
        else:
            raise KeyError(key)

        obj.__parent__ = self
        obj.__name__ = key
        return obj

    def keys(self, do_filter=False, do_sort=False):
        if self.vpath is None:
            return []

        keys = sorted([
            unicode(key) for key in self.frs.listdir(self.vpath)
            if self._filter(key)
        ])

        if not do_filter and not do_sort:
            return keys

        metadata = self.metadata

        if do_filter:
            hidden_keys = metadata.get('exclude', [])
	    hidden_keys.extend(['_*'])
            for key in hidden_keys:
                for _key in fnmatch.filter(keys, key):
                    keys.remove(_key)

        if do_sort:
            sorted_keys = metadata.get('order', [])
            if sorted_keys:
                sorted_keys.reverse()
                for key in sorted_keys:
                    try:
                        keys.remove(key)
                        keys.insert(0, key)
                    except ValueError:
                        # wrong key in config file
                        pass
        return keys

    def get(self, key, default=None):
        try:
            return self._get(key)
        except KeyError:
            return default

    def values(self, do_filter=False, do_sort=False):
        return [self._get(key) for key in self.keys(do_filter, do_sort)]

    def items(self, do_filter=False, do_sort=False):
        return [(key, self._get(key)) for key in self.keys(do_filter, do_sort)]

    def get_recent_file_subpaths(self):
        # 1. 检查是否存在有效的缓存，如果有，直接返回sub_vpath清单
        # ['asdfa/aa.doc', 'asdf.rst']
        #today_str = datetime.date.today().strftime('%Y-%m-%d')
        timenow = [t for t in time.localtime(time.time())[:5]]
        str_timenow = '-'.join(
            [str(t) for t in time.localtime(time.time())[:5]])

        tmp_dir = tempfile.gettempdir()
        cache_name = 'zcmscache' + '-'.join(self.vpath.split('/'))
        cache_path = os.path.join(tmp_dir, cache_name) + '.txt'
        sub_vpaths = []
        cache_is_recent = False
        minutes_lag = 720  # 默认半天

        def lag_minutes(time_now, txt_time):
            tn, tt = time_now[:], txt_time[:]
            to_expend = [0, 0, 75, 0]
            for t in to_expend:
                tn.append(t)
                tt.append(t)
            t1 = time.mktime(tn)
            t2 = time.mktime(tt)
            lag = (t1 - t2) / 60
            return lag

        # try the cache first
	is_debug = get_current_registry().settings.get('pyramid.debug_templates', False)
        if not is_debug and os.path.exists(cache_path):
            rf = file(cache_path, 'r')
            txt_date = rf.readline().rstrip()
            if txt_date != '':
                txt_time = [int(n) for n in txt_date.split('-')]
                if lag_minutes(timenow, txt_time) < minutes_lag:
                    cache_is_recent = True
                    sub_vpaths = [rl.rstrip() for rl in rf.readlines()]
            rf.close()

        # 2. 否则重新查找出来，并更新缓存
        if not cache_is_recent:
            wf = file(cache_path, 'w')
            to_write = str_timenow + '\n'

            sub_time_vpaths = get_sub_time_paths(self, self.vpath)

            def mycmp(x, y):
                if x[0] == '' or y[0] == '':
                    return -1
                return cmp(y[0], x[0])

            # todo
            sub_time_vpaths.sort(mycmp)
            sub_vpaths = [vpath[1] for vpath in sub_time_vpaths]

            for vpath in sub_vpaths:
                to_write += vpath + '\n'
            wf.write(to_write)
            wf.close()
        return sub_vpaths

    def get_obj_by_subpath(self, sub_vpath):
        """ 根据vpath，找到对象 """
        cur = self
        for name in sub_vpath.split('/'):
            if not name:
                pass
            cur = cur.get(name)
        return cur

    def __getitem__(self, key):
        """ traverse """
        return self._get(key)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())


class File(FRSAsset):

    def _get_data(self):
        if self.vpath is None:
            return ''
        else:
            return self.frs.open(self.vpath, 'rb').read()

    def _set_data(self, value):
        if self.vpath is None:
            raise NotImplementedError('Choose first a valid path.')
        else:
            self.frs.open(self.vpath, 'wb').write(value)

    data = property(_get_data, _set_data)

    @property
    def metadata(self):
        return {'title':self.__name__.split('.', 1)[0].replace('-', ' ')}

    @property
    def contentType(self):
        if self.vpath.endswith('html'):
            return 'text/html'
        elif self.vpath.endswith('rst'):
            return 'text/rst'
        elif self.vpath.endswith('md'):
            return 'text/markdown'
        else:
            return 'text/plain'

class Image(File): pass
   
class Page(File):

    @property
    def metadata(self):
        if self._md is None:
            f = self.frs.open(self.vpath, 'rb')
            row = f.readline().strip()
            if row != '---': 
                self._md = {}
                return self._md

            lines = []
            row = f.readline()
	    while row:
                if row.startswith('---'): break
                lines.append(row)
                row = f.readline()
            else:
                self._md = {}
                return self._md

            self._md = yaml.load(''.join(lines))
        return self._md

    def get_body(self):
        f = self.frs.open(self.vpath, 'rb')
        row = f.readline().strip()
        # windows会自动增加utf8的标识字
        if row[0:3] == '\xef\xbb\xbf':
            row = row[3:]
        if row == '---': 
            lines = []
            row = f.readline()
            while row and not row.startswith('---'): 
                row = f.readline()
            row = ''
        return row + '\n' + f.read()

    def render_html(self, request):
        data = self.get_body()

        lstrip_data = data.lstrip()
        if self.__name__.endswith('.rst'):
            # 判断文件内容是否为html
            if lstrip_data and lstrip_data[0] == '<':
                return data

            # 不显示的标题区域，标题在zpt里面独立处理了
            ospath = self.ospath
            return rst2html(data, str(ospath), self, request)
        elif self.__name__.endswith('.md'):
            return ''.join(markdown.Markdown().convert(data.decode('utf8')))

        elif self.__name__.endswith('.html'):
            return data

