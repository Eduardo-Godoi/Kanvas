from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import Facilitator, Instructor

from .models import Course
from .serializers import CourseSerializer


class RegisterCourse(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [Instructor]

    def post(self, request):
        try:
            name = request.data['name']
            course = Course.objects.create(name=name)
            serializer = CourseSerializer(course)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': 'Course with this name already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'errors': f'{str(e)} is missing'},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        courses = Course.objects.all()
        serialized = CourseSerializer(courses, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)


class CourseViewById(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [Instructor]

    def put(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            name = request.data['name']
            course.name = name
            course.save()
            serialeized = CourseSerializer(course)

            return Response(serialeized.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': 'The last course_id does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({'error': 'Course with this name already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'errors': f'{str(e)} is missing'})

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            serializer = CourseSerializer(course)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'errors': 'invalid course_id'},
                            status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            course.delete()
            return Response('', status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            return Response({'errors': 'invalid course_id'},
                            status=status.HTTP_404_NOT_FOUND)


class Registration(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [Instructor]

    def put(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            user_ids = request.data['user_ids']

            course.users.set([])

            for id in user_ids:
                user = User.objects.get(id=id)
                if user.is_staff or user.is_superuser:
                    return Response({'errors': 'Only students can be enrolled in the course.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                course.users.add(user)

            course.save()
            serialized = CourseSerializer(course)

            return Response(serialized.data)
        except TypeError:
            return Response({'errors': 'users_id must be a list'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({'error': 'invalid course_id'},
                            status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': 'invalid user_id list'},
                            status=status.HTTP_404_NOT_FOUND)
