================================
zcms : 基于文件系统的超轻CMS
================================

厌倦了各种复杂的内容管理系统？模版？数据库... 但是sphinx太geek？

作为曾经在CMS系统征战多年的笔者，坚信简单的力量，zcms正是此概念之下的产物：

- 网站内容，直接在文件系统上存放。你可以用任何版本管理系统进行版本管理
- 支持html/rst/md等多种文本格式
- 使用json描述属性
- 模版是纯html
- 完全不需要数据库
- 使用rst指令，输出动态内容

  - 导航数
  - 最新内容
  - blog

demo
===========
- http://everydo.com
- http://edodocs.com
- http://pm.everydo.com
- http://czug.org
- http://zopen.cn

安装
====================

  python bootstrap.py -d
  ./bin/buildout

启动服务
=======================

   ./bin/pserve cms.ini


TODO
================
1. 简化zopen.frs.core的代码，简化json元数据，去除多余的文件夹
2. 支持多种文件类似：

   - html
   - md
   - rst

3. 提供更改内容的api（blog api），方便接入其他后台系统
4. RSS
