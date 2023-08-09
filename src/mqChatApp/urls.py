from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from mqChatApp.views import *

urlpatterns = [
    path("rest_home/", return_custom_home_page, name="rest home page"),
    path("operations/", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="graphQL endpoint")
]