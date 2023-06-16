from django.shortcuts import render
from .models import Message
from .serializers import MessageSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User

# this method create and return list of message
@api_view(['GET','POST'])
def message_list(request, format=None):
    if request.method == 'GET':
        messages = Message.objects.all()
        serializer = MessageSerializer(messages,many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.get(pk=1)
            serializer.save(created_by=user,updated_by=user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# this method update, get and delete one message data
@api_view(['GET','PUT','DELETE'])
def message_detail(request, id, format=None):

    try:
        message = Message.objects.get(pk=id)
    except Message.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = MessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
