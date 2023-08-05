from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import *
from mq_utils import MQUtils
from kombu import Message
import json

class WSConsumer(WebsocketConsumer):
    '''
    receives and send websocket messages
    back to the cleint only.
    message distributing logic would be handled by
    kombu and rabbitMQ
    '''
    def connect(self):
        '''
          accept initial ws connection
          create queue per client
          bind queue to a standby exchange
        '''
        # setup the necessary initials for rabbitMQ
        messaging_properties = MQUtils.default_setup()
        self.publisher = messaging_properties.get("default_publisher")
        self.direct_consumer = messaging_properties.get("direct_consumer").register_callback(self.direct_consumer_callback)
        self.group_consuer = messaging_properties.get("group_consumer").register_callback(self.group_consumer_callback)
        return self.accept()


    def receive(self, txt_data):
        '''
        when you receive a message from a client,
        determine where to publish the message, using the default publisher
        '''
        return self.send()
    # 
    def direct_consumer_callback(self, body, message:Message):
        message.ack()
        self.send(json.dumps(body))
        return print(f"mesage: {message}.\n body:{body}")
    
    def group_consumer_callback(self, body, message:Message):
        message.ack()
        self.send(json.dumps(body))
        return print(f"mesage: {message}.\n body:{body}")
    
    def disconnect(self, code):
        return super().disconnect(code)