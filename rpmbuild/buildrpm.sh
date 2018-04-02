#!/bin/bash

BUILDDIR=`mktemp -d`
RPMROOT=$BUILDDIR/rpmroot
ETC_DIR=$RPMROOT/etc
BIN_DIR=$RPMROOT/usr/bin
APP_DIR=$RPMROOT/var/lib/inventoree
VIRTUALENV_DIR=/var/lib/inventoree/.venv

echo "Cloning Inventoree sources"
git clone https://github.com/viert/inventoree && cd inventoree
git submodule init && git submodule update

export APP_VERSION=$(cat app/__init__.py  | grep VERSION | awk '{ print $NF }' | sed 's/\"//g')
export BUILD_NUMBER=$(git log --oneline | head -1 | awk '{print $1}')

create_dirs() {
	echo "Creating dirs"
	mkdir -p $ETC_DIR
	mkdir -p $BIN_DIR
	mkdir -p $APP_DIR
    mkdir -p $VIRTUALENV_DIR
}

create_virtualenv() {
	echo "Creating virtualenv in $VIRTUALENV_DIR"
	virtualenv $VIRTUALENV_DIR
}

install_requirements() {
	echo "Installing requirements"
	source $VIRTUALENV_DIR/bin/activate
	pip install pathlib2==2.0
	pip install enum34
	pip install backports.shutil-get-terminal-size
	pip install ipython==5.0
	pip install -r requirements.txt
    deactivate
    echo "Moving virtualenv to ${RPMROOT}${VIRTUALENV_DIR}"
    mv $VIRTUALENV_DIR ${RPMROOT}${VIRTUALENV_DIR}
}

install_source_code() {
	echo "Copying inventoree source files"
	for dir in app commands library plugins micro.py wsgi.py; do
		tar c $dir | tar xv -C $APP_DIR
	done
}

build_webui() {
	echo "Building vue.js application"
	mkdir -p $APP_DIR/webui
	pushd webui
	npm i
	npm run build
	tar c dist | tar x -C $APP_DIR/webui/
	popd
}

paste_inventoree_executable() {
	echo "Pasting inventoree executable"
	cat << 'EOF' > $BIN_DIR/inventoree
#!/bin/bash

export CONDUCTOR_ENV=production

INVENTOREE_USER=uwsgi

sudo -E -u $INVENTOREE_USER sh -c "source /var/lib/inventoree/.venv/bin/activate; /var/lib/inventoree/micro.py $*"
EOF
	chmod 755 $BIN_DIR/inventoree
}

install_ext_conf() {
	echo "Installing configs for external services"
	mkdir -p $ETC_DIR/nginx/conf.d
	mkdir -p $ETC_DIR/uwsgi.d
	install -m 0644 extconf/uwsgi/inventoree.ini $ETC_DIR/uwsgi.d/inventoree.ini
	install -m 0644 extconf/nginx/nginx.conf $ETC_DIR/nginx/conf.d/inventoree.conf
}

install_conf() {
	echo "Installing inventoree configs"
	mkdir -p $ETC_DIR/inventoree
	mkdir -p $APP_DIR/config/production
	pushd config/production
	for file in app.py cache.py db.py log.py; do
		cp $file $ETC_DIR/inventoree/$file
		ln -s /etc/inventoree/$file $APP_DIR/config/production/$file
	done
	popd
}

create_rpm() {
	echo "Building RPM"
	fpm -s dir -t rpm \
		--name inventoree \
		--vendor "Inventoree" \
		--version ${APP_VERSION} \
		--iteration ${BUILD_NUMBER} \
		--depends nginx \
		--depends uwsgi \
		--depends uwsgi-plugin-python \
		--depends uwsgi-logger-file \
		--depends mongodb-server \
		--category "Applications/Inventory" \
		--url https://github.com/viert/inventoree \
		--description "Inventoree leads you throught the chaos of your infrastructure" \
		--provides 'config(%{name}) = %{version}-%{release}' \
		--rpm-os linux \
		--architecture x86_64 \
		--config-files etc/inventoree/app.py \
		--config-files etc/inventoree/db.py \
		--config-files etc/inventoree/cache.py \
		--config-files etc/inventoree/log.py \
		--config-files etc/nginx/conf.d/inventoree.conf \
		--config-files etc/uwsgi.d/inventoree.ini \
		-C $RPMROOT
    ls *.rpm
}

create_dirs
create_virtualenv
install_requirements
install_source_code
build_webui
paste_inventoree_executable
install_conf
install_ext_conf
create_rpm
rm -rf $BUILDDIR