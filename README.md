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


## Configuration 

### Static ip

Edit /etc/network/interfaces

```
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
   address X.X.X.X
   netmask 255.255.255.0
   network X.X.X.0
   gateway X.X.X.1
```

### Change computer name

``nano /etc/hosts``
        
```
127.0.0.1     localhost
127.0.1.1     COMPUTER_NAME
```

`` nano /etc/hostname ``

```
COMPUTER_NAME
```

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


