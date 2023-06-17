from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','groups','user_permissions']

class MessageSerializer(serializers.ModelSerializer):
    is_sender = serializers.SerializerMethodField()

    def get_is_sender(self, obj):
        return self.context['user'] == obj.created_by.id
    
    class Meta:
        model = Message
        fields = ['id','content','created_at','is_sender']

class MessageDictSerializer(serializers.Serializer):
    created_by = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    content = serializers.CharField()

    def get_created_by(self, message):
        user = User.objects.get(id=message['created_by'])
        user_serializer = UserSerializer(user)  # Serializer pour l'utilisateur
        return user_serializer.data
    
    class Meta:
        model = Message
        fields = ['id','content','created_at','created_by','user']