from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import *

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
        return self.accept()


    def receive(self, txt_data):
        '''
        when you receive a message from a client,
        determine where to publish the message
        '''
        return self.send()
    
    def disconnect(self, code):
        return super().disconnect(code)