FROM centos as devenvironment
RUN yum install -y epel-release --disableplugin=fastestmirror
RUN yum install -y git python nodejs python-virtualenv ruby-devel gcc-c++ make libffi-devel ruby --disableplugin=fastestmirror
RUN gem install fpm --no-ri --no-rdoc

FROM devenvironment
ADD ./buildrpm.sh /buildrpm.sh
ENTRYPOINT exec ./buildrpm.sh
