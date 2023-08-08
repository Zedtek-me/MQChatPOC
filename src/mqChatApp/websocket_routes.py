from django.urls import re_path
from websocket_handlers import WSConsumer

websocket_urls = [
    re_path(r"^mq_chat/$", WSConsumer.as_asgi(), name="websocket entry point")
]