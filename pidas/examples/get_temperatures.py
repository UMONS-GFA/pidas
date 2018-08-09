from w1thermsensor import W1ThermSensor

for sensor in W1ThermSensor.get_available_sensors():
    print("Sensor {:s} has temperature {:f}° Celsius\n".format(sensor.id, sensor.get_temperature()))

