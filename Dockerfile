FROM cdrx/fpm-centos:7
RUN yum -y install git rsync nmap-ncat python-virtualenv

ADD app /src/app
ADD commands /src/app
ADD config /src/config
ADD extconf /src/extconf
ADD library /src/library
ADD plugins /src/plugins
ADD micro.py /src/micro.py
ADD requirements.txt /src/requirements.txt
ADD wsgi.py /src/wsgi.py
ADD .git /src/.git
ADD build.sh /build.sh
ADD postinst.sh /postinst.sh

ENTRYPOINT /build.sh