# pidas

Data Acquisition System based on Raspberry Pi

### Requirements

* Python 3

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
