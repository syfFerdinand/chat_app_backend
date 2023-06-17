from django.shortcuts import render
from .models import Message
from .serializers import MessageSerializer,MessageDictSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q

# this method create and return list of message
@api_view(['GET','POST'])
def message_list(request, format=None):
    if request.method == 'GET':
        messages = Message.objects.filter(is_deleted=False)
        serializer = MessageSerializer(messages,many=True, context={'request': request,'user':id})
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = MessageSerializer(data=request.data, context={'request': request,'user':id})
        data =request.data.copy()
        if serializer.is_valid():
            user = User.objects.get(pk=data['send_by'])
            to = User.objects.get(pk=data['send_at'])
            serializer.save(created_by=user,updated_by=user,send_at=to)
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
        serializer = MessageSerializer(message, context={'request': request,'user':id})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = MessageSerializer(message, data=request.data, context={'request': request,'user':id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def user_latest_messages(request, id, format=None):
    from django.db.models import Max
    
    messages = Message.objects.filter(
        Q(send_at=id) | Q(created_by=id),
           is_deleted=False
        ).values('created_by').annotate(
        created_at=Max('created_at'),
        content=Max('content'),
        id=Max('id'),
    ).order_by('created_by')
    
    serializer = MessageDictSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def user_messages(request, id, with_id, format=None):
    
    messages = Message.objects.filter(
        (Q(created_by=id) & Q(send_at=with_id)) | (Q(created_by=with_id) & Q(send_at=id)),
        is_deleted=False
    ).order_by('-created_at')
    
    serializer = MessageSerializer(messages, many=True, context={'request': request,'user':id})
    return Response(serializer.data)