---
title: 首页
theme: default.html
---

================================
zcms : 基于文件系统的超轻CMS
================================

厌倦了各种复杂的CMS建站系统？升级，迁移，学习使用... 

zcms, 一个极简的CMS, 无需数据库, 直接在文件系统上存放网站内容

- 支持reStructuredText/markdown，作为页面编写格式
- 扩展reStructuredText指令，来实现动态页面，无需任何“语句”
- 使用yaml描述属性


带来的好处
================
- 内容暴露在文件系统中了，你可以用svn/grep/vi/ulipad/ftp/rsync，你不需要学什么新知识就知道怎么管理内容了！
- 网站内容的编辑人员，也可以做动态页面了！
- 做皮肤的人，不需要麻烦开发人员协助了

其他类似系统的比较
=======================
- sphinx-doc，太geek太死板，写书还行，做网站不适合
- Jekyll吗，做个程序员自己维护的站点还行，公司站点就算了把

扩展的reST指令
=======================
扩展了三个指令::

     .. news::
        :size: 5
        :path: blog

     .. blog::
        :path: blog

     .. nav_tree::
        :root_depth: 2


示例站点
=========
我们易度的所有站点，都采用这个开发完成：

- http://everydo.com
- http://edodocs.com
- http://viewer.everydo.com
- http://czug.org
- http://zopen.cn

