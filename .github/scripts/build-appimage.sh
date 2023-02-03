#!/bin/bash

set -e

# This is a simplified and modified version of a crossplatform kivy build script
# SOURCE: https://github.com/maltfield/cross-platform-python-gui

# Create AppImage root and copy files into it
echo "Extracting python appimage"
chmod +x /tmp/python.AppImage
/tmp/python.AppImage --appimage-extract
mv squashfs-root /tmp/kivy_appdir

# Kivy refuses to build inside the appdir due to missing build deps -> build inside container first
echo "Compiling kivy"
python3 -m pip install "kivy[base] @ https://github.com/kivy/kivy/archive/stable.zip"

# Move the compiled kivy packages into the appdir
echo "Copying kivy into appdir"
mv /home/runner/.local/lib/python3.10/site-packages/kivy /tmp/kivy_appdir/opt/python3.10/lib/python3.10/site-packages/
mv /home/runner/.local/lib/python3.10/site-packages/Kivy-* /tmp/kivy_appdir/opt/python3.10/lib/python3.10/site-packages/

# If pip detects the dependencies in the ubuntu container, it will refuse to install them into the AppImage dir
# -> uninstall them from the container before installing them into the AppImage dir
echo "Uninstalling packages from container"
python -m pip uninstall -y docutils Kivy-Garden pygments pillow
# Install kivy deps into appdir
# Pillow is a dependency of kivy too, even though it is marked as one
echo "Installing dependencies into appdir"
/tmp/kivy_appdir/AppRun -m pip install docutils Kivy-Garden pygments pillow

# Copy main code into appdir
echo "Copying eupnea-initial-setup code into appdir"
mkdir /tmp/kivy_appdir/opt/src
cp -r ./* /tmp/kivy_appdir/opt/src/

# Add AppRun
echo "Replaceing AppRun"
rm /tmp/kivy_appdir/AppRun # Remove old AppRun
cp configs/AppRun /tmp/kivy_appdir/AppRun

# Install xclip into AppRun
# xclip is needed for Kivy on X11 systems
echo "Adding xclip"
cd /tmp
apt-get download xclip # download debian xclip bin
cd ~
mkdir /tmp/xclip
dpkg-deb -R /tmp/xclip*.deb /tmp/xclip # extract bin
cp /tmp/xclip/usr/bin/* /tmp/kivy_appdir/usr/bin/ # copy executables from deb

# Build AppImage
echo "Building AppImage"
chmod +x /tmp/appimagetool.AppImage # make appimagetool executable
/tmp/appimagetool.AppImage /tmp/kivy_appdir /tmp/eupnea-initial-setup.AppImage
