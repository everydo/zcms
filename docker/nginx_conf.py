# -*- coding: utf-8 -*-

""" 根据站点的配置文件，生成nginx的配置 

- input: /var/sites/contents/sites/_config.yaml
- output: /etc/nginx/sites-enabled/zcms.conf:

"""

import os
import yaml

nginx_conf = """server{
    listen 80;
    location  /  {
        proxy_set_header        HOST $http_host;

        rewrite ^/themes/(.*) /themes/$1 break;

        proxy_pass     http://127.0.0.1:8000;
        proxy_redirect off;
    }
}

%s
"""

if __name__ == '__main__':
    sites_config = []
    for site_name in os.listdir('/var/sites/contents/'):
        config = file('/var/sites/contents/%s/_config.yaml' % site_name, 'r')
        site_config = yaml.load(config)
        if site_config['domain_name']:
            sites_config.append("""server{
                listen 80;
                server_name %s;
                location  /  {
                proxy_set_header        HOST $http_host;
                rewrite ^/themes/(.*) /themes/$1 break;
                proxy_set_header        X-ZCMS-VHM true;

                rewrite ^/(.*) /%s/$1 break;

                proxy_pass     http://127.0.0.1:8000;
                proxy_redirect off;
                }
                }""" % (site_config['domain_name'], site_name))

    open('/etc/nginx/sites-enabled/zcms.conf', 'w').write(nginx_conf % '\n'.join(sites_config))
