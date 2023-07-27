import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()


class RabbitMqServerConfig:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        

class RabbitMqProducer:
    def __init__(self, config):

        self.config = config
        self._credentails = pika.PlainCredentials(self.config.user, self.config.password)
        self._connection = pika.BlockingConnection( 
                                                    pika.ConnectionParameters(host= self.config.host,
                                                                                port = self.config.port, 
                                                                                credentials= self._credentails))
        print(f' connection {self._connection}')
        self._channel = self._connection.channel()

        

    def publish(self, queueName, message):
        
        self._channel.queue_declare(queue=queueName, durable=True)
        self._channel.basic_publish(exchange='', 
                                    routing_key= queueName, 
                                    body= json.dumps(message),
                                    properties=pika.BasicProperties())
        self._connection.close()
config = RabbitMqServerConfig(
                                    host=os.getenv('RABBITMQ_HOST'),
                                    port = os.getenv('RABBITMQ_PORT'),
                                    user=os.getenv('RABBITMQ_USER'),
                                    password=os.getenv('RABBITMQ_PASSWORD')
                                )
    
messagePublisher = RabbitMqProducer(config)


