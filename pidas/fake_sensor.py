import datetime
from calendar import timegm
import random


class Fake1WireSensor:
    """Generic fake 1-Wire sensor"""
    def __init__(self, seller_id='00-00000'):
        """Generate a unique id with hexadecimal timestamp"""
        self.id = seller_id + hex(timegm(datetime.datetime.now().utctimetuple()))[3:]


class FakeTempSensor(Fake1WireSensor):
    """Fake 1-Wire temperature sensor default is DS18B20"""
    def __init__(self):
        Fake1WireSensor.__init__(self, seller_id='28-00000')
        self.name = 't'
        self.temperature = 0

    def set_name(self, new_name):
        self.name = new_name

    def get_temperature(self):
        self.temperature = random.uniform(20, 28)
        return self.temperature


def main():
    s = FakeTempSensor()
    print("Temperature of {:s} is {:.3f}".format(s.id, s.get_temperature()))


if __name__ == '__main__':
    main()