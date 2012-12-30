================================
zcms : 基于文件系统的超轻CMS
================================

厌倦了各种复杂的内容管理系统？皮肤？数据库... 你说sphinx，太geek、太死板了吧？

作为曾经在CMS系统征战多年的笔者，坚信简单的力量，zcms正是此概念之下的产物：

- 不需要管理后台，网站内容，直接在文件系统上存放
- 不需要php/asp/jsp/zpt，直接扩展reStructureText，来制作动态页面- 支持html/rst/md等多种文本格式
- 使用json描述属性
- 模版是纯html
- 完全不需要数据库
- powered by pyramid!

带来的好处：

- 内容暴露在文件系统中了，你可以用svn/grep/vi/ulipad/ftp/rsync，你不需要学什么新知识就知道怎么管理内容了！
- 网站内容的编辑人员，也可以做动态页面了！
- 做皮肤的人，不需要麻烦开发人员协助了

扩展的reST指令包括:

     .. news::
     .. blog::
     .. nav_tree::


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

制作新站点
=================
- 网站内容, 参看: sites/demo
- 默认皮肤 themes/bootstrap/index.html
- 可在metadata.json中自定义 theme_url

demo/.frs/metadata.json
--------------------------------------------
网站的整体配置，导航数的顺序和显示也在这里配置

demo/.frs/index.rst.json 首页内容设置
-------------------------------------------------
描述了首页index.rst的信息，内容如下
 
    {
      "left_col":".. include:: indexcol.rst",
      "right_col":"",
      "description": "",
      "title": "易度，带您进入互联网工作时代！"
    }

说明：

在"main"下面有一个"left_col"，它指定了左列，".. include:: indexcol.rst"指的是左列内容包含在index.rst所属目录下的indexcol.rst中。
在indexcol.rst中通过".. raw:: html"指令加入边栏html代码。
"right_col"就是右列，设置方法如上。
文件夹导航树：

在.frs/products.json有如下内容：

    {
      "left_col": ".. navtree::\n   :root_depth: 2",
      "hidden_keys": [
          "img",
          "index.rst"
      ],
      "description": "",
      "title": "产品信息"
    }

说明：

- "left_col": ".. navtree::\n :root_depth: 2"，这一行表示在products的所有未设置
- "left_col"的子文件或子文件夹的视图都会有左列，且左列包含了导航树。 
- ":root_depth: 2"表示从contents文件夹开始的第二级文件夹作为导航树的根，显示根以下的当前内容的父目录及兄弟目录。
- "hidden_keys"字段包含的是不想在导航树中显示的子目录或子文件。

注：

- "left_col"、"right_col"都是向下传递的,或者说是向上依赖的。
- 即，某一文件页面没设置"left_col"，但显示了左列，那是因为它的父目录有设置"left_col"，要让它不显示，可以设置"left_col":""。 所以，如果要某个目录下的所有页面显示左右列，只需在这个目录的matadata.json中设置左右列。
.frs文件夹包含了.frs文件夹所在目录之下的其他目录或文件的信息。

reStructuredText写法入门介绍：http://karronqiu.googlepages.com/ReStructuredText_Primer.html。

TODO
================
0. 和github集成，github修改后直接更新网站
1. 提供更改内容的api（blog api？）
2. 支持markdown
3. 提供RSS
4. 缓存，减少对文件系统的访问，减少metadata解析
5. 生成的html，符合Bootstrap的规范
6. blog指令不知道为何不能工作，而且分页需要重写

