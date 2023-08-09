from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework import status
import json
# Create your views here.


def return_custom_home_page(req):
    return HttpResponse("This only returns a custom home page, indicating an entry point where all rest requests go.")