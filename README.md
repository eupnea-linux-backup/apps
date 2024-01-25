# THE EUPNEA PROJECT HAS BEEN DISCONTINUED

Please use one of the following projects instead:
* MrChromebox's UEFI/RW_L (turn chromebook into almost a normal laptop): https://mrchromebox.tech/#fwscript
* FyraLab's submarine (does not require firmware modification): https://github.com/FyraLabs/submarine

<details>
<summary>View the old readme</summary>

# Apps

Distro + toolkit independent GUI apps for EupneaOS and Depthboot.  
Written with the [kivy](https://kivy.org/) python gui framework.
The appimage build scripts is based
on [cross-platform-python-gui](https://github.com/maltfield/cross-platform-python-gui).

## Eupnea-setup

Initial setup app, similar to gnome-initial-setup, but distro-agnostic.

## Eupnea-settings

Settings app for Eupnea specific options. Not intended to replace the system settings app.

## Disclaimer

These apps are not designed/intended to be run on non depthboot systems. **DO NOT** just run it on
your system as it might override some settings and/or damage your OS!!! Run it in a virtual machine.

## How to run the apps for debugging/developing

1. Install pip.
2. Install kivy with pip: `pip install kivy`
3. Clone the repo and run the apps main.py with python3.10 or later.
