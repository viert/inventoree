#!/bin/bash

export APPNAME=inventoree
export PROJECT_DIR=/src
export BUILD_ROOT=/buildroot
export USRLIB_DIR=/usr/lib/$APPNAME
export VIRTUALENV_DIR=$USRLIB_DIR/.venv
export WWWDIR=/var/www/inventoree
export ETCDIR=/etc/inventoree
export PROJECT_SOURCE_ITEMS="app commands library plugins micro.py wsgi.py"
export REPO=c7-mntdev-x64

copy_sources() {
    echo "Copying project sources"

    DESTDIR=${BUILD_ROOT}${USRLIB_DIR}
    mkdir -p $DESTDIR
    mkdir -p $DESTDIR/config/production
    pushd $PROJECT_DIR

    echo "Copying python sources"
    for dir in $PROJECT_SOURCE_ITEMS; do
        tar c $dir | tar xv -C $DESTDIR
    done

    echo "Copying and symlinking configs"
    mkdir -p ${BUILD_ROOT}${ETCDIR}
    pushd config/production
    for f in app.py cache.py db.py log.py; do
        cp $f ${BUILD_ROOT}${ETCDIR}
        ln -s ${ETCDIR}/$f $DESTDIR/config/production/$f
    done
    popd

    echo "Copying ext software configs"
    mkdir -p ${BUILD_ROOT}/etc/nginx/conf.d
    mkdir -p ${BUILD_ROOT}/etc/uwsgi.d
    cp extconf/nginx/nginx.conf ${BUILD_ROOT}/etc/nginx/conf.d/$APPNAME.conf
    cp extconf/uwsgi/inventoree.ini ${BUILD_ROOT}/etc/uwsgi.d/$APPNAME.ini
    popd
}

cleanup_buildroot() {
    pushd ${BUILD_ROOT}

    echo "Removing *.pyc files"
    find . -name '*.pyc' -delete

    echo "Removing .git* files"
    find . -name '.git*' -delete

    echo "Removing unused authorizers"
    rm -f ${BUILD_ROOT}${USRLIB_DIR}/plugins/authorizers/sys_authorizer.py
    rm -f ${BUILD_ROOT}${USRLIB_DIR}/plugins/authorizers/vk_authorizer.py

    echo "Removing unused plugins"
    rm -f ${BUILD_ROOT}${USRLIB_DIR}/plugins/commands/example.py
    rm -f ${BUILD_ROOT}${USRLIB_DIR}/plugins/commands/cmdb.py
    popd
}

copy_virtualenv() {
    echo "Copying virtualenv"
    mkdir -p ${BUILD_ROOT}${VIRTUALENV_DIR}
    pushd $VIRTUALENV_DIR
    tar c * | tar xv -C ${BUILD_ROOT}${VIRTUALENV_DIR}
    popd
}

paste_executable() {
    echo "Pasting executable"
    mkdir -p ${BUILD_ROOT}/usr/bin
    EXECUTABLE=${BUILD_ROOT}/usr/bin/$APPNAME
    cat << 'EOF' > $EXECUTABLE
#!/bin/bash

export MICROENG_ENV=production

MICROENG_USER=uwsgi

sudo -E -u $MICROENG_USER sh -c "source /usr/lib/inventoree/.venv/bin/activate; /usr/lib/inventoree/micro.py $*"
EOF
    chmod 755 $EXECUTABLE
}

build_rpm() {
    pushd $PROJECT_DIR
    gitcommit=`git rev-list --tags --max-count=1`
    export VERSION=`git describe --tags $gitcommit`
    export BUILD=`git rev-list $VERSION.. --count`
    echo ${VERSION}-${BUILD} > ${BUILD_ROOT}${USRLIB_DIR}/app/__version__
    popd
    echo "======= BUILDING RPM PACKAGE ======="
    fpm -s dir -t rpm \
        --name $APPNAME \
        --vendor "Mail.Ru Infrastructure Services" \
        --version ${VERSION} \
        --iteration ${BUILD} \
        --depends nginx \
        --depends uwsgi \
        --depends uwsgi-plugin-python \
        --depends python \
        --depends inventoree-auth-sys \
        --depends inventoree-plugin-cmdb-import \
        --category "Admin/Inventory" \
        --url https://github.com/viert/inventoree \
        --description "Inventoree leads you through the chaos of your infrastructure" \
        --provides 'config(%{name}) = %{version}-%{release}' \
        --rpm-os linux \
        --architecture x86_64 \
        --config-files etc/$APPNAME/app.py \
        --config-files etc/$APPNAME/cache.py \
        --config-files etc/$APPNAME/db.py \
        --config-files etc/$APPNAME/log.py \
        --config-files etc/nginx/conf.d/$APPNAME.conf \
        --config-files etc/uwsgi.d/$APPNAME.ini \
        --after-install /postinst.sh \
        -C ${BUILD_ROOT}
}

push_rpm() {
    PKG=$APPNAME-$VERSION-$BUILD.x86_64.rpm
    echo $PKG
    rsync "$PKG" mntdev@pkg.corp.mail.ru::$REPO/ && echo $REPO | nc pkg.corp.mail.ru 15222
}

copy_sources
copy_virtualenv
cleanup_buildroot
paste_executable
build_rpm
push_rpm
