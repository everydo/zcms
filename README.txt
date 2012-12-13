================================
内容管理网站zcms 使用方法
================================

安装：

  python bootstrap.py -d
  ./bin/buildout

启动服务

   ./bin/pserve cms.ini


TODO:

1. 简化zopen.frs.core的代码，简化json元数据，去除多余的文件夹
2. 支持多种文件类似：

   - html
   - md
   - rst

3. 提供更改内容的api（blog api），方便接入其他后台系统
