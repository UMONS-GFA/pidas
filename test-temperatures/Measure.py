from collections import OrderedDict


class Measure:
    def __init__(self):
        self.sensorID = None
        self.sensorName = ''
        self.measureType = ''
        self.measureAcquire = ''
        self.measureUnit = None
        self.value = None
        self.valueTime = None

    def to_json(self):
        json_object = OrderedDict()
        json_object["sensorID"] = self.sensorID
        json_object["sensorName"] = self.sensorName
        json_object["measureType"] = self.measureType
        json_object["measureAcquire"] = self.measureAcquire
        json_object["measureUnit"] = self.measureUnit
        json_object["value"] = self.value
        json_object["valueTime"] = self.valueTime

        return json_object


class TempMeasure(Measure):
    def __init__(self, sensor_id, value, value_time):
        Measure.__init__(self)
        self.sensorID = sensor_id
        self.sensorName = 'Temperature'
        self.measureType = 'numeric'
        self.measureAcquire = 'sample'
        self.measureUnit = 'degree Celsius'
        self.value = value
        self.valueTime = value_time