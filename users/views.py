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

            user = User.objects.create_user(**request.data)
            serializer = UserSerializer(user)
            output = {
                **serializer.data,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }

            return Response(output, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'msg': 'User already exists'}, status=status.HTTP_409_CONFLICT)

class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']

            user = authenticate(username=username, password=password)

            if user != None:
                token = Token.objects.get_or_create(user=user)[0]
                return Response({'token': token.key})
            
            return Response({'msg': 'Wrong username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        except KeyError as e:
            return Response({'msg': f'{str(e)} is missing'})
