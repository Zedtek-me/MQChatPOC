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
        # create a queue for every user on startup
        self.current_user_queue = MQUtils.create_user_direct_queue(name=self.scope.get("user").username)
        self.publisher = messaging_properties.get("default_publisher")
        self.direct_consumer = messaging_properties.get("direct_consumer").register_callback(self.direct_consumer_callback)
        self.group_consumer = messaging_properties.get("group_consumer").register_callback(self.group_consumer_callback)
        self.direct_exchange = messaging_properties.get("direct_exchange")
        self.group_exchange = messaging_properties.get("group_exchange")
        return self.accept()


    def receive(self, txt_data):
        '''
        when you receive a message from a websocket client,
        determine where to publish the message, using the default publisher
        '''
        data = json.loads(txt_data)
        message = data.get("message")
        routing_key = data.get("routing_key")
        # To send a message to a friend, use the name of the friend as the routing_key, 
        # since every user's queue is bound to the default direct exchange using their names as the routing keys.
        # To send to a group, get the group name or its routing key from the group db, then use that as your routing key
        self.publisher.publish(
            {"message_to_publish": message},
            routing_key=routing_key,
            exchange=self.direct_exchange
                               )
        # there might not be a need to re-send the message here again, since the
        # callback in the consumer is already doing that for us.
        # self.send(json.dumps(message))

        # creating a group:
        # MQUtils.create_user_group_queue(username=self.scope.get("user").username, group_name="Scientific_Research", new_group=True)

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