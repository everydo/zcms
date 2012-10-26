================================
内容管理网站zopen.cms 使用方法
================================

环境要求：
----------
 . 需要 Python 2.4或更高版本

 . 安装virtaulenv、repose.bfg ( http://docs.everydo.com/zope3/bfg/install.rst有说明)
   $ virtualenv --no-site-packages bfgenv   
     //  --no-site-packages 来产生virtualenv是关键的. 这个标记对运行 repoze.bfg 所需要的包提供了必要的隔离. 

 . 在Virtualenv:bfgenv中安装 repoze.bfg及deliverance
   $ cd virtualenv( bfgenv )目录
   $ bin/easy_install -i http://dist.repoze.org/lemonade/dev/simple repoze.bfg

 . 在Virtualenv:bfgenv中安装 deliverance
   $ bin/easy_install pip
   $ bin/pip install http://deliverance.openplans.org/dist/Deliverance-snapshot-latest.pybundle
   或者可以：
   $ source ...bfg_enviroment_path/bin/activate 
   $ easy_install http://dist.repoze.org/lemonade/dev/Deliverance-0.2.tar.gz
 

服务启用：
----------
 . 启用虚拟环境
   $ source ...bfg_enviroment_path/bin/activate 

 . 在zopen.cms目录及其他依赖包目录下，安装cms包及其依赖包
   $ python setup.py develop

 . 启动服务
   $ paster serve cms.ini








