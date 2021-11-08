import pdb

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserSerializer


class CreateUserView(APIView):
    def post(self, request):
        try:
            data = request.data
            user = User.objects.create_user(**data)
            serialized = UserSerializer(user)

            return Response(serialized.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'conflict': 'User already registered'}, status=status.HTTP_409_CONFLICT)


class LoginView(APIView):
    def post(self, request):
        data = request.data
        user = authenticate(**data)

        if user:
            token = Token.objects.get_or_create(user=user)[0]
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response({'message': 'Invalid Credentials'},
                        status=status.HTTP_401_UNAUTHORIZED)
