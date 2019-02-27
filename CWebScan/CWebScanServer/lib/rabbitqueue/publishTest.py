import pika
import logging

# logging.basicConfig(level=logging.DEBUG)

credentials = pika.PlainCredentials('guest', 'guest')
parameters =  pika.ConnectionParameters('localhost', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.exchange_declare(exchange="message", exchange_type="topic")

channel.basic_publish('message', 'example.text', 'This is message')
