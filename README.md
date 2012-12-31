================================
zcms : 基于文件系统的超轻CMS
================================

*大量简化中，请稍后使用*

厌倦了各种复杂的内容管理系统？皮肤？数据库... 

作为曾经在CMS系统征战多年的笔者，坚信简单的力量，zcms正是此概念之下的产物：

- 不需要管理后台，网站内容，直接在文件系统上存放, 完全不需要数据库
- 支持reST/md作为页面编写格式
- 直接扩展reStructureText，来实现动态页面，无需任何“语句”
- 使用yaml描述属性
- powered by pyramid!

带来的好处：

- 内容暴露在文件系统中了，你可以用svn/grep/vi/ulipad/ftp/rsync，你不需要学什么新知识就知道怎么管理内容了！
- 网站内容的编辑人员，也可以做动态页面了！
- 做皮肤的人，不需要麻烦开发人员协助了

其他类似系统的比较：

- sphinx-doc，太geek太死板，写书还行，做网站不适合
- Jekyll吗，做个程序员自己维护的站点还行，公司站点就算了把

扩展的reST指令
=====================
     .. news::
        :size: 5
        :path: blog

     .. blog::
        :path: blog

     .. nav_tree::
        :root_depth: 2

root_depth: 表示从第二级文件夹作为导航树的根

demo sites
===========
我们易度的所有站点，都采用这个开发完成：

- http://everydo.com
- http://edodocs.com
- http://viewer.everydo.com
- http://czug.org
- http://zopen.cn

安装
====================

    python bootstrap.py -d
    ./bin/buildout

启动服务
=======================

    ./bin/pserve production.ini

制作站点: sites/demo
============================
站点数据结构
--------------------
TODO：吸收jekell的yaml配置方法，简化使用

     _config.yaml
     index.rst
     _index_upper.rst
     tour/
	_config.yaml
        _upper.rst
        _left.rst
	index.rst
	install.rst
	sites.rst
     blog/
        _config.yaml
        _upper.rst
        _left.rst
	index.rst
        post01.rst
        post02.rst
     about.rst
     _about_upper.rst

配置站点属性 _config.yaml
--------------------------------------------
网站的整体配置，导航数的顺序和显示也在这里配置:

      theme_base: http://localhost:6543/themes/bootstrap # 皮肤存放的url基准地址, 如果需要换肤，改变这个就行
      theme_default: defualt.html # 默认的皮肤
      hidden: img                 # 隐藏的内容, 不在导航树中显示
          index.rst
      ordered:                    # 固定排序

首页内容yaml设置
-------------------------------------------------
描述了首页index.rst的信息，内容如下
 
      title: 易度，带您进入互联网工作时代！
      description: 
      left: indexcol.rst # 左列展示文件indexcol.rst
      right:  # 右侧列
      upper:  # 上方行

TODO
================
0. 和github集成，github修改后直接更新网站
1. 提供更改内容的api（blog api？）
2. 提供RSS
3. 缓存，减少对文件系统的访问，减少metadata解析
