#!/bin/bash

# This is a simplified and modified version of a crossplatform kivy build script
# SOURCE: https://github.com/maltfield/cross-platform-python-gui

# Create AppImage root and copy files into it
chmod +x /tmp/python.AppImage
/tmp/python.AppImage --appimage-extract
mv squashfs-root /tmp/kivy_appdir

# Kivy refuses to build inside the appdir due to missing build deps -> build inside container first
python3 -m pip install "kivy[base] @ https://github.com/kivy/kivy/archive/stable.zip"

# Move the compiled kivy packages into the appdir
mv /home/runner/.local/lib/python3.10/site-packages/kivy /tmp/kivy_appdir/opt/python3.10/lib/python3.10/site-packages/
mv /home/runner/.local/lib/python3.10/site-packages/Kivy.libs /tmp/kivy_appdir/opt/python3.10/lib/python3.10/site-packages/
mv /home/runner/.local/lib/python3.10/site-packages/Kivy-* /tmp/kivy_appdir/opt/python3.10/lib/python3.10/site-packages/

# Install kivy deps into the appimage
# If pip detects the dependencies in the container, it will refuse to install them into the AppImage dir
# -> uninstall them from the container before installing them into the AppImage dir
python -m pip uninstall docutils Kivy-Garden pygments
# Install kivy deps into appdir
/tmp/kivy_appdir/AppRun -m pip install docutils Kivy-Garden pygments

# Copy main code into appdir
cp ./* /tmp/kivy_appdir/opt/

# Add AppRun
rm /tmp/kivy_appdir/AppRun # Remove old AppRun
cp configs/AppRun /tmp/kivy_appdir/AppRun

# Build AppImage
chmod +x /tmp/appimagetool.AppImage # make appimagetool executable
/tmp/appimagetool.AppImage /tmp/kivy_appdir /tmp/eupnea-initial-setup.AppImage
chmod +x /tmp/eupnea-initial-setup.AppImage
