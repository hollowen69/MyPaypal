from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def drink_list(request, format=None):

    if request.method == 'GET':
        return Response("hello")


