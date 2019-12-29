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
# The initial backoff time after a disconnection occurs, in seconds.
minimum_backoff_time = 1
# The maximum backoff time before giving up, in seconds.
MAXIMUM_BACKOFF_TIME = 32
# Whether to wait with exponential backoff before publishing.
should_backoff = False
client = None
jwt_iat = None
jwt_exp_mins = None

logging.config.fileConfig("logging.conf")
# create logger
logger = logging.getLogger("mylogger")
logger.info("Start Google IoT Core adapter...")    


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

    logger.debug('Creating JWT using {} from private key file {}'.format(
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

    # After a successful connect, reset backoff time and stop backing off.
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    logger.info('on_disconnect', error_str(rc))

    # Since a disconnect occurred, the next loop iteration will wait with
    # exponential backoff.
    global should_backoff
    should_backoff = True


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    logger.debug('on_publish - mid: ' + str(unused_mid))


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload.decode('utf-8'))
    logger.debug('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id, cloud_region, registry_id, device_id)
    logger.info("Creating client...")
    logger.info('Device client_id is \'{}\''.format(client_id))
    
    global client
    
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
    

def send_data_from_bound_device(
        service_account_json, project_id, cloud_region, registry_id, device_id,
        gateway_id, num_messages, private_key_file, algorithm, ca_certs,
        mqtt_bridge_hostname, mqtt_bridge_port, jwt_expires_minutes, payload):
    """Sends data from a gateway on behalf of a device that is bound to it."""
    logger.info("Sending to Google IoT Core...")
    # [START send_data_from_bound_device]
    global minimum_backoff_time
    global should_backoff

    # Publish device events and gateway state.
    device_topic = '/devices/{}/{}'.format(device_id, 'events')
  
    global client
    global jwt_iat
    global jwt_exp_mins
    
    if jwt_iat is None:
        jwt_iat = datetime.datetime.utcnow()
    jwt_exp_mins = jwt_expires_minutes
    seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
    if seconds_since_issue > 60 * jwt_exp_mins:
        logger.debug('Refreshing token after {}s'.format(seconds_since_issue))
        jwt_iat = datetime.datetime.utcnow()
        client = get_client(
            project_id, cloud_region, registry_id, gateway_id,
            private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
            mqtt_bridge_port)
    if client is None:
        jwt_iat = datetime.datetime.utcnow()
        client = get_client(
            project_id, cloud_region, registry_id, device_id,
            private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
            mqtt_bridge_port)

    # Publish num_messages messages to the MQTT bridge
    #client.loop()

    if should_backoff:
        # If backoff time is too large, give up.
        if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
            logger.error('Exceeded maximum backoff time. Giving up.')
            client = None
            minimum_backoff_time = 1
            should_backoff = False
            return

        delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
        time.sleep(delay)
        minimum_backoff_time *= 2
        client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    mqttinfo= client.publish(
            device_topic, '{} : {}'.format(device_id, payload), qos=1)
    logger.debug("mid: " + str(mqttinfo.mid) + " - is_published: " + str(mqttinfo.is_published()))
    client.loop()

    logger.info('sent...')
    # [END send_data_from_bound_device]

def main():
    
    send_data_from_bound_device(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), "cloudmind4home",
            "europe-west1", "cloudmind4home", "RASP_000000001b982f0d",
            "", 100, "../../security/rsa_private.pem",
            "RS256", "../../security/roots.pem", "mqtt.googleapis.com",
            8883, 20, "Hello data!")
    
    send_data_from_bound_device(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), "cloudmind4home",
            "europe-west1", "cloudmind4home", "RASP_000000001b982f0d",
            "", 100, "../../security/rsa_private.pem",
            "RS256", "../../security/roots.pem", "mqtt.googleapis.com",
            8883, 20, "Hello data!")
    return
    print('Finished.')


if __name__ == '__main__':
    main()
