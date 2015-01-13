## 2015-01-09 Connect a DS18B20 and retrieve temperature
http://www.framboise314.fr/mesure-de-temperature-1-wire-ds18b20-avec-le-raspberry-pi/

### Hardware connections

![DS1820 pinout](https://github.com/UMONS-GFA/pidas/tree/master/doc/sensors/temperature/DS18B20/DS18B20-pinout.jpg)

![Raspberry Pi Cobler pinout](https://github.com/UMONS-GFA/pidas/blob/master/doc/sensors/temperature/DS18B20/schema_connexion.jpg)

### Raspberry configuration

Activate the kernel modules
```
sudo modprobe w1-gpio
sudo modprobe w1-therm
```

Test if modules are loaded
``` 
lsmod | grep w1 
```
Get temperature from all sensors
```
cat /sys/bus/w1/devices/28-*/w1_slave

6a 01 4b 46 7f ff 06 10 5f : crc=5f YES
6a 01 4b 46 7f ff 06 10 5f t=22625
68 01 4b 46 7f ff 08 10 05 : crc=05 YES
68 01 4b 46 7f ff 08 10 05 t=22500
6b 01 4b 46 7f ff 05 10 49 : crc=49 YES
6b 01 4b 46 7f ff 05 10 49 t=22687
```



It works with three DS18B20. Two close to Pi and one at 4 meters of the Pi.


