import ssl
import pika
import time
from os import environ
from logging import getLogger

logger = getLogger()

isTest = True

if environ.get("stage") == "test":
    HOSTNAME = "rabbitmq"
    PORT = 5672

# Create a connection and channel
retry_timer = 2
while True:
    try:
        if isTest:
            parameters = pika.ConnectionParameters(
                host=HOSTNAME,
                port=PORT,
                virtual_host='/')
        else:
            credentials = pika.PlainCredentials(USERNAME, PASSWORD)
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            options = pika.SSLOptions(context)
            parameters = pika.ConnectionParameters(host=HOSTNAME, port=PORT,
                                                   virtual_host='/',
                                                   credentials=credentials,
                                                   ssl_options=options
                                                   )

        connection = pika.BlockingConnection(parameters)
        logger.info("Connected to Rabbit MQ SUCCESS!")
        print("Connected to Rabbit MQ SUCCESS!")
        break
    except Exception:
        logger.info(f"Connecting to RabbitMQ Failed... Retrying in {retry_timer} seconds")
        print(f"Connecting to RabbitMQ Failed... Retrying in {retry_timer} seconds")
        time.sleep(retry_timer)
        retry_timer += 2

logger.info("Connected")

print('CONNECTED!')

# Create an AMQP topic exchange for Notifications

channel = connection.channel()
exchange_name = "greenharbor.topic"
exchange_type = "topic"
channel.exchange_declare(exchange=exchange_name,
                         exchange_type=exchange_type, durable=True)

queue_name = 'Workshop_Registration_Notification'
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchange_name,
                   queue=queue_name, routing_key='workshop.register')

queue_name = 'Workshop_Withdrawal_Notification'
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchange_name,
                   queue=queue_name, routing_key='workshop.withdraw')

queue_name = 'Logging'
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchange_name,
                   queue=queue_name, routing_key='#')

connection.close()
