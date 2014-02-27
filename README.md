================================
zcms : 基于文件系统的超轻CMS
================================
厌倦了各种复杂的CMS建站系统？厌倦了升级，迁移，学习管理... 

然而，Sphinx-doc太单调太简单了，Jekyll也还是太复杂...

那么zcms来了, 一个极简的CMS，都是你熟悉的:

- 无需数据库, 每个页面是一个文本文件
- 扩展reStructuredText指令(.rst)，轻松实现博客、导航、新闻等动态内容
- 支持Markdown格式(.md)编写页面
- 当然支持html页面(.html)
- 支持多站点

zcms吸取了Jekyll优点，使用python/pyramid开发完成，完全无需任何开发知识即可掌握. 

欢迎微博传播，如有反馈，请微博联系: http://weibo.com/panjunyong

使用docker安装： https://index.docker.io/u/panjunyong/zcms/

开发调试代码
===================
使用本地代码(/home/panjy/git/zcms):

    docker run -t -i -v /home/panjy/git/zcms:/opt/zcms/ -p 8000:80 zcms shell
    bin/buildout
    bin/pserve development.ini

无阻力建站
============================
站点放在sites文件夹内容，每个站点包括内容（contents）和皮肤（themes）

设置栏目顺序和标题
-----------------------
每个文件夹下，可以放置一个 `_config.yaml` 的文件，在这里设置文件夹的属性:

    title: 教程                                 # 标题
    order: [index.rst, tour, blog, about.rst]   # 显示顺序
    exclude: [img]                                 # 隐藏图片文件夹的显示


对于rst/md的页面文件, 可直接在文件头部指定这些信息:

    ---
    title: 教程                                 # 标题
    creator: 潘俊勇                             # 创建人
    created: 2010-12-12 9:12                    # 创建时间，新闻根据这个时间排序
    ---

页面文件的属性，必须以三个短横开始和结束

设置左右列以及头部区域
--------------------------
对整个文件夹下的页面模版，可以定制左侧、右侧和头部的显示信息，分别加入： `_left.rst` , `_right.rst` , `_upper.rst` 

如果具体某个页面，需要定制，也可以单独设置，通过命名来区分：

1. index.rst 页面的头部信息 `_upper_index.rst`
2. about.rst 页面的左侧信息 `_left_about.rst`

动态内容
-------------
可在reST中使用如下指令即可：

1. 最近新闻

         .. news::
            :size: 5
            :path: blog

2. 博客页面

         .. blogs::
            :size: 20

3. 导航树

         .. navtree::
            :root_depth: 2

外观模版的设置
---------------------
在站点根文件夹下面的_config.yaml里面，定义了整个站点的皮肤

    theme_base: http://localhost:6543/themes/bootstrap  # 存放模版的基准位置，这里可能存放了多个模版
    theme: default.html                                  # 默认的模版

外观模版是通过一个网址来指定的，上面的完整外观模版地址是：

    http://localhost:6543/themes/bootstrap/default.html

如果不想使用默认的外观模版，可文件夹或页面属性中，设置个性化的外观模版:

    theme: home.html     # 首页模版，可能没有左右列

这里会使用外观模版:

    http://localhost:6543/themes/bootstrap/home.html

制作外观模版
-----------------
可看看themes文件夹里面的文件，其实就是一个python的String Template.

一个最基础的外观模版可以是：


     <html>
       <head>
          <title>$title - $site_title</title>
          <meta name="Description" content="$site_description"/>
       </head>
       <body>
          <ul>$nav</ul>
          <div>$upper</div>
          <table>
            <tr>
               <td>$left</td>
               <td>$content</td>
               <td>$right</td>
            </tr>
          </table>
       </body>
     </html>

这个文件里面可以包括如下变量:

- `site_title` : 站点的标题
- `site_description` : 当前内容的描述信息
- `nav` : 站点的导航栏目
- `title` : 当前内容的标题
- `description` : 当前内容的描述信息
- `content` : 当前内容正文
- `left` : 左侧列显示的内容
- `right` : 右侧列显示的内容
- `upper` : 上方区域显示的内容
- `theme_base` : 外观模版的所在的位置

nginx虚拟主机
=======================
1. 参考zcms-nginx/nginx.conf, 编写自己需要的nginx站点配置，放入文件夹 /home/panjy/zcms-nginx
2. 启动nignx:

     docker run -d -p 8001:80 -v /home/panjy/zcms-nginx/:/etc/nginx/sites-enabled --name nginx dockerfile/nginx

默认安装，我们得到的地址首页是

     http://server.com:6543/site_name

如果我们希望实际类似这样访问

     http://site_name.server.com

zcms也可以在uwsgi下运行，配置方法与nginx虚拟主机类似:

1. nginx.conf, 改为使用uwsgi

2. 运行uwsgi --ini uwsgi.ini， uwsgi默认调用9010端口


Jekyll参考
===================

- http://www.ruanyifeng.com/blog/2012/08/blogging_with_jekyll.html
- http://yanping.me/cn/blog/2012/03/18/github-pages-step-by-step/
- http://www.soimort.org/posts/101/

TODO
================
1. 默认的bootstrap风格皮肤还很弱，还没有支持right列
2. production模式下，应该大量缓存加速，减少io
3. 提供webdav api
4. 提供RSS输出
5. 使用zapian进行全文搜索、排序等
