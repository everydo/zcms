# encoding: utf-8

""" 根据站点的配置文件，生成nginx的配置 

- input: /var/sites
- output: /etc/nginx/sites-enabled/zcms.conf:

server{
    listen 80;
    location  /  {
        # uwsgi设置
        # uwsgi_param SCRIPT_NAME ""; 
        # include uwsgi_params;
        # uwsgi_pass 127.0.0.1:9010;

        # 设置静态皮肤的访问，也可以改为直接由nginx提供下载
        rewrite ^/themes/(.*) /themes/$1 break;
 
        # 通知zcms开启虚拟主机功能
        # 根站点
        if ($host = domain.com){
            proxy_set_header        HOST $host:8001;
            proxy_set_header        X-ZCMS-VHM true;
            rewrite ^/(.*) /demo/$1 break;
        }
 
        proxy_pass     http://127.0.0.1:8000;
        proxy_redirect off;
    }
}       
"""
