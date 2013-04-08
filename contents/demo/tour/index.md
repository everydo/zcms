---
title: 快速教程
description: 这里加上一些用于SEO的文字
---
快速教程
===============

安装
-------

      python bootstrap.py -d
      ./bin/buildout

启动服务
--------------

      ./bin/pserve production.ini

站点数据结构
--------------------

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

