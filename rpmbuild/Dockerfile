FROM centos
ADD ./buildrpm.sh /buildrpm.sh
RUN yum install -y epel-release --disableplugin=fastestmirror
RUN yum install -y git python nodejs python-virtualenv ruby-devel gcc-c++ make libffi-devel ruby --disableplugin=fastestmirror
RUN gem install fpm --no-ri --no-rdoc
ENTRYPOINT exec ./buildrpm.sh
