# pidas

Raspberry Pi configuration to interact with Data Acquisition Systems

## Installation 

[Download](https://github.com/debian-pi/raspbian-ua-netinst/releases) last version of debian netinstall

Copy img file to sd card

```sudo dd bs=4m if=PATH_TO_IMG of=/dev/DEVNAME```

Copy *installer-config.txt* to sd card

Insert the sd card into the raspberry pi and make sure to have network connection

Power up the Pi

Wait during netinstall

## Usage

Warning:  The layout is QWERTY

Login: root  

Password: raspbian 


## Raspberry Pi configuration 

### Load required modules at startup 

Edit /etc/modules and add w1-gpio and w1-therm at the end of the file
```
snd-bcm2835                                                           
w1-gpio                                                            
w1-therm   
```

Restart the Pi and check if modules are loaded.
```
lsmod | grep w1
```

### Set static ip

Edit /etc/network/interfaces

```
iface lo inet loopback
#iface eth0 inet dhcp
iface eth0 inet static
   address X.X.X.X
   netmask 255.255.255.0
   network X.X.X.0
   gateway X.X.X.1
```
