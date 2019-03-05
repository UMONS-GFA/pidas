import datetime
import re
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient, exceptions
from gfa_logging import MsgLogger
from pidas.settings import DATABASE, MQTT_CONFIG

msg_logger = MsgLogger(date_formatter=True)

influx_client = InfluxDBClient(DATABASE['HOST'], DATABASE['PORT'], DATABASE['USER'], DATABASE['PASSWORD'],
                               DATABASE['NAME'])


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""

    client.subscribe(MQTT_CONFIG['topic'] + '+')


def on_log(client, userdata, level, buf):
    msg_logger.logger.debug(buf)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server"""

    msg_logger.logger.info(msg.topic+" " + str(msg.payload.decode('utf-8')))
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %Z')
    sensor_id = re.split(MQTT_CONFIG['topic'], msg.topic)
    json_body = [
        {
            "measurement": DATABASE['MEASUREMENT'],
            "tags": {
                "sensorID": sensor_id[1]
            },
            "fields": {
                "value": float(msg.payload.decode('utf-8')),
                "time": str(current_time)
            }
        }
    ]
    msg_logger.logger.debug(json_body)
    try:
        msg_logger.logger.info("Writing to influx")
        influx_client.write_points(json_body)
    except exceptions.InfluxDBClientError as e:
        msg_logger.logger.error("{}".format(e.content))


def main():

    client = mqtt.Client(client_id=MQTT_CONFIG['bridge_client_id'])
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_log = on_log
    client.connect(MQTT_CONFIG['server'], MQTT_CONFIG['port'], MQTT_CONFIG['keepalive'])
    client.loop_forever()


if __name__ == '__main__':
    main()
