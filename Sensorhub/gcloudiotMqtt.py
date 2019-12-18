#!/usr/bin/env python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Python sample for connecting to Google Cloud IoT Core via MQTT, using JWT.
This example connects to Google Cloud IoT Core via MQTT, using a JWT for device
authentication. After connecting, by default the device publishes 100 messages
to the device's MQTT topic at a rate of one per second, and then exits.
Before you run the sample, you must follow the instructions in the README
for this sample.
"""

# [START iot_mqtt_includes]
import argparse
import datetime
import logging
import os
import random
import ssl
import time

import jwt
import paho.mqtt.client as mqtt
# [END iot_mqtt_includes]

logging.config.fileConfig("logging.conf")
# create logger
logger = logging.getLogger("mylogger")
logger.info("Start sensing...")


# [START iot_mqtt_jwt]
def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
        Args:
         project_id: The cloud project ID this device belongs to
         private_key_file: A path to a file containing either an RSA256 or
                 ES256 private key.
         algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
        Returns:
            A JWT generated from the given project_id and private key, which
            expires in 20 minutes. After 20 minutes, your client will be
            disconnected, and a new JWT will have to be generated.
        Raises:
            ValueError: If the private_key_file does not contain a known key.
        """

    token = {
            # The time that the token was issued at
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
            algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)
# [END iot_mqtt_jwt]


# [START iot_mqtt_config]
def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    logger.info('on_connect', mqtt.connack_string(rc))

def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    logger.error('on_disconnect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    logger.info('on_publish')


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload.decode('utf-8'))
    logger.info('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # The topic that the device will receive commands on.
    mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)

    # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
    logger.info('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client
# [END iot_mqtt_config]


def detach_device(client, device_id):
    """Detach the device from the gateway."""
    # [START iot_detach_device]
    detach_topic = '/devices/{}/detach'.format(device_id)
    print('Detaching: {}'.format(detach_topic))
    client.publish(detach_topic, '{}', qos=1)
    # [END iot_detach_device]


def attach_device(client, device_id, auth):
    """Attach the device to the gateway."""
    # [START iot_attach_device]
    attach_topic = '/devices/{}/attach'.format(device_id)
    attach_payload = '{{"authorization" : "{}"}}'.format(auth)
    client.publish(attach_topic, attach_payload, qos=1)
    # [END iot_attach_device]

def send_data_from_bound_device(
        project_id, cloud_region, registry_id, device_id,
        private_key_file, algorithm, ca_certs, payload):
    """Sends data from a gateway on behalf of a device that is bound to it."""
    # [START send_data_from_bound_device]
    # Publish device events and gateway state.
    device_topic = '/devices/{}/{}'.format(device_id, 'state')
    gateway_topic = '/devices/{}/{}'.format("", 'state')


    mqtt_bridge_hostname = "mqtt.googleapis.com"
    mqtt_bridge_port = 8883
    # Use gateway to connect to server
    client = get_client(
        project_id, cloud_region, registry_id, device_id,
        private_key_file, algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port)

    attach_device(client, device_id, '')
    logger.info('Waiting for device to attach.')
    time.sleep(5)

    # Publish state to gateway topic
    gateway_state = 'Starting gateway at: {}'.format(time.time())
    logger.info(gateway_state)
    client.publish(gateway_topic, gateway_state, qos=1)

    # Publish num_messages messages to the MQTT bridge
    client.loop()

    logger.info('Publishing message: \'{}\' to {}'.format(payload, device_topic))
    client.publish(device_topic, '{} : {}'.format(device_id, payload), qos=1)
    client = get_client(project_id, cloud_region, registry_id, device_id, private_key_file, algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port)

    time.sleep(5)

    detach_device(client, device_id)

    logger.info('data sent...')
    # [END send_data_from_bound_device]