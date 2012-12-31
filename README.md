================================
zcms : 基于文件系统的超轻CMS
================================
厌倦了各种复杂的CMS建站系统？厌倦了升级，迁移，学习管理... 

然而，Sphinx-doc太单调太简单了，Jekyll也还是太复杂...

那么zcms来了, 一个极简的CMS，都是你熟悉的:

- 无需数据库, 每个页面是一个文本文件
- 扩展reStructuredText指令，来实现动态页面
- 支持Markdown格式编写页面

zcms吸取了Jekyll优点，使用python/pyramid开发完成，完全无需任何开发知识即可掌握

启动服务
=======================
站点制作，启动：

    ./bin/pserve development.ini

正式使用，启动：

    ./bin/pserve production.ini


示例站点
=========
我们易度的所有站点，都采用这个开发完成：

- http://everydo.com
- http://edodocs.com
- http://viewer.everydo.com
- http://czug.org
- http://zopen.cn

无阻力建站
============================
1. 创建站点文件夹

   站点默认放置在sites文件夹下，比如sites/demo

2. 填充站点内容

   在站点文件夹下创建子文件夹和页面，子文件夹将自动成为子栏目, index.rst或index.md自动成为子栏目的首页:

     demo/
        index.rst
        tour/
           index.rst
           install.rst
           sites.rst
        blog/
           index.rst
           post01.rst
           post02.rst
        about.rst
        img/
           logo.png

文件夹和页面属性
===========================
你可站点基本可以工作, 存在的问题：

- 栏目顺序比较随机无序
- 栏目标题是文件名，可能需要中文标题

每个文件夹下，可以放置一个 _config.yaml 的文件，在这里设置文件夹的属性:

    title: 教程                                 # 标题
    order: [index.rst, tour, blog, about.rst]   # 显示顺序
    hide: [img]                                 # 隐藏图片文件夹的显示

在站点下面的_config.yaml里面，还定义了整个站点的皮肤

    theme_base: http://localhost:6543/themes/bootstrap/  # 存放模版的基准位置，这里可能存放了多个模版
    theme_default: default.html                          # 默认的模版

对于rst/md的页面文件, 可直接在文件头部指定这些信息:

    ---
    title: 教程                                 # 标题
    ---

页面文件的属性，必须以三个短横开始和结束


设置左右列以及头部信息
========================
对整个文件夹下的页面模版，可以定制左侧、右侧和头部的显示信息，分别加入：

1. _left.rst
2. _right.rst
3. _upper.rst

如果具体某个页面，需要定制，也可以单独设置，通过命名来区分：

1. index.rst 页面的头部信息 _upper_index.rst
2. about.rst 页面的左侧信息 _left_about.rst

动态内容
=======================
可在reST中使用如下指令即可：

1. 最近新闻

         .. news::
            :size: 5
            :path: blog

2. 博客页面

         .. blog::
            :path: blog

3. 导航数

         .. nav_tree::
            :root_depth: 2

