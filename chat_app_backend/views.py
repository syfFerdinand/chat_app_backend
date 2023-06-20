from django.shortcuts import render
from .models import Message, User
from .serializers import MessageSerializer, UserSerializer, MessageDictSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Max


def verify_token_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Extraire le token d'accès de l'en-tête Authorization
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]

            # Valider et authentifier le token d'accès
            authentication = JWTAuthentication()
            validated_token = authentication.get_validated_token(access_token)

            # Décoder le token d'accès pour obtenir les informations de l'utilisateur
            user_id = validated_token.payload["user_id"]

            # Récupérer l'objet utilisateur à partir de votre modèle User
            user = User.objects.get(id=user_id)

            # Passer l'objet utilisateur à la méthode de la classe d'API
            kwargs["user"] = user

            # Appeler la méthode de la classe d'API
            return view_func(request, *args, **kwargs)

        # Le token d'accès est invalide ou manquant, renvoyer une réponse d'erreur
        return Response(
            {"detail": "Token d'accès invalide"}, status=status.HTTP_401_UNAUTHORIZED
        )

    return wrapper


# this method create and return list of message
@api_view(["GET", "POST"])
@verify_token_required
def message_list(request, user, format=None):
    if request.method == "GET":
        messages = Message.objects.filter(is_deleted=False)
        serializer = MessageSerializer(
            messages, many=True, context={"request": request, "user": user.id}
        )
        return Response(serializer.data)

    if request.method == "POST":
        serializer = MessageSerializer(
            data=request.data, context={"request": request, "user": user.id}
        )
        data = request.data.copy()
        if serializer.is_valid():
            to = User.objects.get(pk=data["send_at"])
            serializer.save(created_by=user, updated_by=user, send_at=to)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# this method update, get and delete one message data
@api_view(["GET", "PUT", "DELETE"])
@verify_token_required
def message_detail(request, user, format=None):
    try:
        message = Message.objects.get(pk=id)
    except Message.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = MessageSerializer(
            message, context={"request": request, "user": id}
        )
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = MessageSerializer(
            message, data=request.data, context={"request": request, "user": id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@verify_token_required
def user_latest_messages(request, user, format=None):
    messages = (
        Message.objects.filter(
            Q(send_at=user.id) | Q(created_by=user.id), is_deleted=False
        )
        .values("created_by")
        .annotate(created_at=Max("created_at"), content=Max("content"))
        .order_by("-created_at")
    )

    serializer = MessageDictSerializer(messages, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@verify_token_required
def user_messages(request, user, with_id, format=None):
    messages = Message.objects.filter(
        (Q(created_by=user.id) & Q(send_at=with_id))
        | (Q(created_by=with_id) & Q(send_at=user.id)),
        is_deleted=False,
    ).order_by("created_at")

    serializer = MessageSerializer(
        messages, many=True, context={"request": request}
    )
    return Response(serializer.data)


@api_view(["GET"])
@verify_token_required
def user_list(request, user, format=None):
    users = User.objects.all()
    serializer = UserSerializer(
        users, many=True, context={"request": request}
    )
    return Response(serializer.data)


@api_view(["POST"])
def user_create(request, format=None):
    serializer = UserSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# this method update, get and delete one user data
@api_view(["GET", "PUT", "DELETE"])
@verify_token_required
def user_detail(request, user, format=None):
    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data)

    elif request.method == "PUT":
        data = request.data.copy()
        serializer = UserSerializer(
            user, data=data['user'], context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
