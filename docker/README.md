================================
zcms : 基于文件系统的超轻CMS
================================
zcms是一个极简的基于文件系统CMS，都是你熟悉的:

- 无需数据库, 每个页面是一个文本文件
- 扩展reStructuredText指令(.rst)，轻松实现博客、导航、新闻等动态内容
- 支持Markdown格式(.md)编写页面

示例站点:

- http://viewer.everydo.com
- http://developer.everydo.com
- http://everydo.com
- http://edodocs.com

运行自带的demo站点(8000端口访问):

    docker run -d -p 8000:80 panjunyong/zcms

运行自己位于/home/panjy/sites的站点::

    docker run -d -v /home/panjy/sites:/var/sites -p 8000:80 panjunyong/zcms

调试站点皮肤（即时刷新，但是运行速度较慢）:

    docker run -d -v /home/panjy/sites:/var/sites -p 8000:80 panjunyong/zcms debug

站点详细使用，参看: http://github.com/everydo.com/zcms
