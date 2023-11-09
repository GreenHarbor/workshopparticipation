import os
import json
import requests
import amqp_setup
import pika
from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

if os.environ.get("stage") == "test":
    workshop_service_url = os.environ.get('workshop_service_url')

get_user_lambda_url = os.environ.get('get_user_lambda_url')
get_all_users_lambda_url = os.environ.get('get_all_users_lambda_url')
get_user_lambda_url = ""
get_all_users_lambda_url = ""

app = Flask(__name__)

CORS(app)


@app.route("/health")
def health_check():

    return jsonify(
        {
            "message": "Service is healthy.",
            "service:": "workshop-participation",
        }
    ), 200


@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    response = requests.get(get_all_users_lambda_url)

    if response.status_code != 200:
        return jsonify(
            {
                "message": "Unable to get creator email",
            }
        ), 500

    users = response.json()['data']
    for user in users:
        if user['username'] == data['user_id']:
            email = user['email']
    if os.environ.get("stage") == "test":
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.patch(
            workshop_service_url + '/workshop/register/' + str(data['creator_id']) + "/" + str(data['creation_timestamp']),
            data=json.dumps({
                "User_Id": str(data['user_id'])
            }),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            # verify=False
        )
    else:
        response = requests.patch(
            workshop_service_url + '/workshop/register/' + str(data['creator_id']) + "/" + str(data['creation_timestamp']),
            data=json.dumps({
                "User_Id": str(data['user_id'])
            }),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            # verify=False
        )

    if response.status_code != 200:
        return jsonify(
            {
                "message": "Unable to register for workshop.",
            }
        ), 500

    notification_data = {
        "email": email,
        "title": data["title"],
        "date": data["start_timestamp"]
    }

    print(notification_data)
    connection = pika.BlockingConnection(amqp_setup.parameters)

    channel = connection.channel()

    channel.basic_publish(
        exchange=amqp_setup.exchange_name, routing_key="workshop.register",
        body=json.dumps(notification_data),
        properties=pika.BasicProperties(delivery_mode=2))

    connection.close()

    return jsonify(
        {
            "message": response.json()['message']
        }
    ), 200


@app.route("/withdraw", methods=['POST'])
def withdraw():

    data = request.get_json()

    response = requests.get(get_all_users_lambda_url)
    if response.status_code != 200:
        return jsonify(
            {
                "message": "Unable to get creator email",
            }
        ), 500

    users = response.json()['data']
    # print(users)
    # email = "test"
    for user in users:
        if user['username'] == data['creator_id']:
            email = user['email']
    print(email)

    if os.environ.get("stage") == "test":
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.patch(
            workshop_service_url + '/workshop/withdraw/' + str(data['creator_id']) + "/" + str(data['creation_timestamp']),
            data=json.dumps({
                "User_Id": str(data['user_id'])
            }),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            # verify=False
        )
    else:
        response = requests.patch(
            workshop_service_url + '/workshop/withdraw/' + str(data['creator_id']) + "/" + str(data['creation_timestamp']),
            data=json.dumps({
                "User_Id": str(data['user_id'])
            }),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            # verify=False
        )
    if response.status_code != 200:
        return jsonify(
            {
                "message": "Unable to withdraw from workshop.",
            }
        ), 500

    notification_data = {
        "title": data["title"],
        "email": email,
    }
    connection = pika.BlockingConnection(amqp_setup.parameters)
    channel = connection.channel()

    channel.basic_publish(
        exchange=amqp_setup.exchange_name, routing_key="workshop.withdraw",
        body=json.dumps(notification_data),
        properties=pika.BasicProperties(delivery_mode=2))

    connection.close()

    return jsonify(
        {
            # "message": "Withdrawal successful.",
            "message": response.json()['message']
        }
    ), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
