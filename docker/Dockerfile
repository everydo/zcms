FROM ubuntu:12.04

MAINTAINER panjunyong@gmail.com

RUN echo "deb http://mirrors.ustc.edu.cn/ubuntu precise main universe" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install python-dev python-pip && \
    apt-get install -y software-properties-common && \
    apt-get -y clean all 

# 安装nginx
RUN add-apt-repository -y ppa:nginx/stable
RUN apt-get update
RUN apt-get install -y nginx
RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf

# 安装build环境
RUN mkdir mkdir -p /opt/buildout-cache/eggs 
RUN pip install -i http://pypi.douban.com/simple/ --upgrade setuptools 
RUN pip install -i http://pypi.douban.com/simple/ zc.buildout

RUN mkdir -p /var/zcms/
ADD buildout.cfg /var/zcms/buildout.cfg
ADD production.ini /var/zcms/production.ini
ADD development.ini /var/zcms/development.ini
ADD nginx_conf.py /var/zcms/nginx_conf.py
ADD sites /var/sites

# 先更新setuptools再安装fts_web
WORKDIR /var/zcms
RUN python -c "from zc.buildout import buildout; buildout.main(['bootstrap'])" && \
    bin/buildout 

ADD run /usr/local/bin/run
RUN chmod +x /usr/local/bin/run
RUN /usr/share/locales/install-language-pack en_US

# Attach volumes.
VOLUME /var/log/nginx

EXPOSE 80

CMD ["start"]
ENTRYPOINT ["/usr/local/bin/run"]
