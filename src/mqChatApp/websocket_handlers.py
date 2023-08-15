from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import *
from .mq_utils import MQUtils
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
        self.accept()
        # setup the necessary initials for rabbitMQ
        self.messaging_properties = MQUtils()
        # create a queue for every user on startup
        print("setting up necessary messaging implementations...")
        self.current_user_queue = self.messaging_properties.create_user_direct_queue(name=self.scope.get("user").username if self.scope.get("user") else "NoUser")
        self.publisher = self.messaging_properties.get_default_publisher()
        self.direct_consumer = self.messaging_properties.get_direct_consumer().register_callback(self.direct_consumer_callback)
        self.group_consumer = self.messaging_properties.get_group_consumer().register_callback(self.group_consumer_callback)
        self.direct_exchange = self.messaging_properties.default_direct_exchange()
        # self.group_exchange = messaging_properties.get
        print("messaging functionality setup done!")


    def receive(self, text_data):
        '''
        when you receive a message from a websocket client,
        determine where to publish the message, using the default publisher
        '''
        # data = json.loads(txt_data)
        # message = data.get("message")
        # routing_key = data.get("routing_key")
        message = text_data
        # To send a message to a friend, use the name of the friend as the routing_key, 
        # since every user's queue is bound to the default direct exchange using their names as the routing keys.
        # To send to a group, get the group name or its routing key from the group db, then use that as your routing key
        self.publisher.publish(
            {"message_to_publish": message},
            routing_key="NoUser",
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
        self.messaging_properties.connection.release()
        return super().disconnect(code)