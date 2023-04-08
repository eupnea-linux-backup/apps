#!/bin/bash

set -e

# This is a simplified and modified version of a cross-platform kivy build script
# SOURCE: https://github.com/maltfield/cross-platform-python-gui

# Create AppImage root and copy files into it
echo "Extracting python appimage"
chmod +x /tmp/python.AppImage
/tmp/python.AppImage --appimage-extract
mv squashfs-root /tmp/kivy_appdir

# Kivy refuses to build inside the appdir due to missing build deps -> build inside container first
echo "Compiling kivy"
# Download kivy stable zip
curl -L https://github.com/kivy/kivy/archive/stable.zip -o /tmp/kivy.zip
unzip /tmp/kivy.zip -d /tmp/
# Edit kivy setup.py to enable wayland and x11 support
sed "0,/c_options['use_wayland'] = False/s//c_options['use_wayland'] = True/" /tmp/kivy-stable/setup.py
sed "0,/c_options['use_x11'] = False/s//c_options['use_x11'] = True/" /tmp/kivy-stable/setup.py
# compile kivy
python3 -m pip install /tmp/kivy-stable/[base]

# Move the compiled kivy packages into the appdir
echo "Copying kivy into appdir"
mv /home/runner/.local/lib/python3.10/site-packages/kivy /tmp/kivy_appdir/opt/python3.10/lib/python3.10/site-packages/
mv /home/runner/.local/lib/python3.10/site-packages/Kivy-* /tmp/kivy_appdir/opt/python3.10/lib/python3.10/site-packages/

# If pip detects the dependencies in the ubuntu container, it will refuse to install them into the AppImage dir
# -> uninstall them from the container before installing them into the AppImage dir
echo "Uninstalling packages from container"
python3 -m pip uninstall -y docutils Kivy-Garden pygments pillow
# Install kivy deps into appdir
# Pillow is a dependency of kivy too, even though it is marked as one
echo "Installing dependencies into appdir"
/tmp/kivy_appdir/AppRun -m pip install docutils Kivy-Garden pygments pillow

# Unpack non python deps into appdir
echo "Installing non python dependencies"
# make dirs
mkdir /tmp/{xclip,libsdl2,libsdl2-image,libdecor,libjpeg-turbo8,libtiff5,libjbig0,libdeflate0}
# xclip is needed for Kivy on X11 systems
# libsdl2 dependencies are needed on some systems
# libjpeg-turbo8 is needed on Fedora
apt-get download xclip libsdl2-2.0-0 libsdl2-image-2.0-0 libjpeg-turbo8 libdecor-0-0 libtiff5 libjbig0 libdeflate0
# extract debs
dpkg-deb -R ./xclip*.deb /tmp/xclip
dpkg-deb -R ./libsdl2-2.0-0*.deb /tmp/libsdl2
dpkg-deb -R ./libsdl2-image-2.0-0*.deb /tmp/libsdl2-image
dpkg-deb -R ./libdecor-0-0*.deb /tmp/libdecor
dpkg-deb -R ./libjpeg-turbo8*.deb /tmp/libjpeg-turbo8
dpkg-deb -R ./libtiff5*.deb /tmp/libtiff5
dpkg-deb -R ./libjbig0*.deb /tmp/libjbig0
dpkg-deb -R ./libdeflate0*.deb /tmp/libdeflate0
rm *.deb # remove debs
# copy binaries into appdir
cp -r /tmp/xclip/usr/bin /tmp/kivy_appdir/usr
cp -r /tmp/libsdl2/usr/lib/* /tmp/kivy_appdir/usr/lib
cp -r /tmp/libsdl2-image/usr/lib/* /tmp/kivy_appdir/usr/lib
cp -r /tmp/libdecor/usr/lib/* /tmp/kivy_appdir/usr/lib
cp -r /tmp/libjpeg-turbo8/usr/lib/* /tmp/kivy_appdir/usr/lib
cp -r /tmp/libtiff5/usr/lib/* /tmp/kivy_appdir/usr/lib
cp -r /tmp/libjbig0/usr/lib/* /tmp/kivy_appdir/usr/lib
cp -r /tmp/libdeflate0/usr/lib/* /tmp/kivy_appdir/usr/lib

# Clean appdir
echo "Uninstalling unneeded python dependencies from appdir"
/tmp/kivy_appdir/AppRun -m pip uninstall -y wheel build setuptools urllib3 tomli pyproject_hooks pkg_resources packaging idna charset_normalizer certifi
/tmp/kivy_appdir/AppRun -m pip uninstall -y pip

# Copy main code into appdir
echo "Copying eupnea-initial-setup code into appdir"
mkdir /tmp/kivy_appdir/opt/src
cp -r ./eupnea-setup/* /tmp/kivy_appdir/opt/src/
# Copy crash handler into appdir
cp -r ./crash-handler /tmp/kivy_appdir/opt/src/

# Add AppRun
echo "Replaceing AppRun"
rm /tmp/kivy_appdir/AppRun # Remove old AppRun
cp configs/AppRun /tmp/kivy_appdir/AppRun

# Build AppImage
echo "Building AppImage"
chmod +x /tmp/appimagetool.AppImage # make appimagetool executable
/tmp/appimagetool.AppImage /tmp/kivy_appdir /tmp/eupnea-setup.AppImage
