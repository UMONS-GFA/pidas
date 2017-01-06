#!/usr/bin/env bash

echo "Creating user pi…"
useradd pi -m -p raspberry
usermod -aG dialout pi


echo "Getting usb ids for Arduino…"
# Search for the keyword Arduino and print the sixth column of that line
vendorInfo=$(lsusb | awk '/Arduino/ {print $6}')
idVendor=${vendorInfo:0:4}
idProduct=${vendorInfo:5:4}
symlink="USBT001"
echo "Writting vendor info..."
echo "SUBSYSTEM=='tty', ATTRS{idVendor}==$idVendor, ATTRS{idProduct}==$idProduct, SYMLINK=$symlink" > /etc/udev/rules.d/99-usb_serial.rules
