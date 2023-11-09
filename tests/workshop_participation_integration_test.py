import ssl
import pika
import unittest
import time
from os import environ
import pytest
from src import amqp_setup
import json
import requests

class TestRabbitMQIntegration(unittest.TestCase):
    def test_rabbitmq_connection(self):
        hostname = "b-d9b47cdf-9f98-427e-b1ef-c0f3c02bcce0.mq.ap-southeast-1.amazonaws.com"
        port = "5671"

        # Extract credentials from environment variables
        username = environ.get('rabbitmq_username', "admin")
        password = environ.get('rabbitmq_password', "admingreenharbor")

        SSL_ENABLED = True  # Change this based on your configuration

        if SSL_ENABLED:
            credentials = pika.PlainCredentials(username, password)
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            parameters = pika.ConnectionParameters(
                host=hostname,
                port=port,
                virtual_host='/',
                credentials=credentials,
                ssl_options=pika.SSLOptions(context),
            )
        else:
            parameters = pika.ConnectionParameters(host=hostname, port=port)

        connected = False
        start_time = time.time()
        print('Connecting...')
        while not connected:
            try:
                connection = pika.BlockingConnection(parameters)
                connected = True
            except pika.exceptions.AMQPConnectionError:
                if time.time() - start_time > 20:
                    self.fail("Connection failed")
                    break  # Exit the loop after the specified time

        # Add assertions to check connection status or other relevant behavior
        self.assertTrue(connected, "Connection should be established")

        # Clean up resources
        if connected:
            connection.close()

def call(client, path, method='GET', body=None):
    mimetype = 'application/json'

    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype,
    }

    if method == 'POST':
        response = client.post(path, data=json.dumps(body), headers=headers)
    elif method == 'PUT':
        response = client.put(path, data=json.dumps(body), headers=headers)
    elif method == 'PATCH':
        response = client.patch(path, data=json.dumps(body), headers=headers)
    elif method == 'DELETE':
        response = client.delete(path)
    else:
        response = client.get(path)

    return {
        "json": json.loads(response.data.decode('utf-8')),
        "code": response.status_code
    }


@pytest.mark.dependency()
def test_register_no_signin(client):
    test_fixture= {
        "user_id": "2",
        "creator_id": "1",
        "title": "title",
        "creation_timestamp": "2023-10-20-01:47:36.472",
        "start_timestamp": "2023-10-20-01:47:36.472"
    }

    result = call(client, 'register', "POST", body=test_fixture)

    assert result['code'] == 200 or result['code'] == 500

@pytest.mark.dependency()
def test_register_no_creator_id(client):
    test_fixture= {
        "user_id": "2",
        "creator_id": "1000000000",
        "title": "title",
        "creation_timestamp": "2023-10-20-01:47:36.472",
        "start_timestamp": "2023-10-20-01:47:36.472"
    }

    result = call(client, 'register', "POST", body=test_fixture)

    assert result['code'] == 500

@pytest.mark.dependency()
def test_register_no_user_id(client):
    test_fixture= {
        "user_id": "1000000000",
        "creator_id": "1",
        "title": "title",
        "creation_timestamp": "2023-10-20-01:47:36.472",
        "start_timestamp": "2023-10-20-01:47:36.472"
    }

    result = call(client, 'register', "POST", body=test_fixture)

    assert result['code'] == 500

@pytest.mark.dependency()
def test_register_missing_body(client):
    test_fixture= {
        "creator_id": "",
        "creation_timestamp": "",
        "user_id": "",
    }

    result = call(client, 'register', "POST", body=test_fixture)

    assert result['code'] == 500

if __name__ == '__main__':
    unittest.main()
