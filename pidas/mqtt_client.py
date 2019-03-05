import paho.mqtt.client as mqtt
from time import time, sleep
from gfa_logging import MsgLogger
from pidas.settings import MQTT_CONFIG
from w1thermsensor import W1ThermSensor, SensorNotReadyError, NoSensorFoundError

msg_logger = MsgLogger(date_formatter=True)


def on_connect(client, userdata, flags, rc):

    """ The callback for when the client receives a CONNACK response from the server."""

    client.subscribe(MQTT_CONFIG['topic'] + '+')


def on_message(client, userdata, msg):

    """The callback for when a PUBLISH message is received from the server"""

    msg_logger.logger.info(msg.topic + " " + str(msg.payload.decode('utf-8')))


def main():
    msg_logger.logger.info('_____ Started _____')

    client = mqtt.Client(client_id=MQTT_CONFIG['client_id'])
    client.on_connect = on_connect
    client.on_message = on_message
    msg_logger.logger.info("connecting to broker…")
    client.connect(MQTT_CONFIG['server'], MQTT_CONFIG['port'], MQTT_CONFIG['keepalive'])
    client.loop_start()
    while True:
        for sensor in W1ThermSensor.get_available_sensors():
            timestamp = int(time())
            try:
                temperature = sensor.get_temperature()
                # row = "{},{},{}".format(sensor.id, temperature, timestamp)
                tp = MQTT_CONFIG['topic'] + str(sensor.id)
                #msg_logger.logger.info("Publishing message to topic", str(tp))
                client.publish(topic=tp, payload=temperature)

            except SensorNotReadyError as e:
                msg_logger.logger.error(e)
            except NoSensorFoundError as e:
                msg_logger.logger.error(e)
            sleep(5)
    client.loop_stop()


if __name__ == '__main__':
    main()
