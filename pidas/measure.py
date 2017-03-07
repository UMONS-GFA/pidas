from collections import OrderedDict


class Measure:
    def __init__(self):
        self.sensor_id = None
        self.sensor_name = ''
        self.value = None
        self.value_time = None

    def to_json(self):
        json_object = OrderedDict()
        json_object["sensorID"] = self.sensor_id
        json_object["sensorName"] = self.sensor_name
        json_object["value"] = self.value
        json_object["valueTime"] = self.value_time

        return json_object


class TempMeasure(Measure):
    def __init__(self, sensor_id, sensor_name, value, value_time):
        Measure.__init__(self)
        self.sensor_id = sensor_id
        self.sensor_name = sensor_name
        self.value = value
        self.value_time = value_time
