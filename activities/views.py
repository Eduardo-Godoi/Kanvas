from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.permissions import Facilitator, Instructor

from .models import Activity, Submission
from .serializers import ActivitySerializer, SubmissionSerializer


class ViewActivity(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [Facilitator]

    def post(self, request):
        try:
            # title = request.data['title']
            # points = request.data['points']
            activity = Activity.objects.create(**request.data)
            serializer = ActivitySerializer(activity)

            output = serializer.data
            submissions = output.pop('submission_set')
            output['submissions'] = submissions

            return Response(output, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': 'Activity with this name already exists'},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        if not user.is_staff:
            return Response('', status=status.HTTP_403_FORBIDDEN)

        activities = Activity.objects.all()
        serializer = ActivitySerializer(activities, many=True)

        output = []

        for item in serializer.data:
            activitie = {**item}
            submissions = activitie.pop('submission_set')
            activitie['submissions'] = submissions
            output.append(activitie)

        return Response(output, status=status.HTTP_200_OK)


class ActivityViewById(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [Facilitator]

    def put(self, request, activity_id):
        try:
            activity = Activity.objects.get(id=activity_id)

            if activity.submission_set.first():
                return Response({'error': 'You can not change an Activity with submissions'},
                                status=status.HTTP_400_BAD_REQUEST)

            activity.title = request.data['title']
            activity.points = request.data['points']
            activity.save()

            serializer = ActivitySerializer(activity)
            output = {**serializer.data}
            submissions = output.pop('submission_set')
            output['submissions'] = submissions

            return Response(output, status=status.HTTP_200_OK)

        except IntegrityError:
            return Response({'error': 'Activity with this name already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'errors': f'{str(e)} is missing'})
        except Activity.DoesNotExist:
            return Response({'errors': 'Invalid activity_id'},
                            status=status.HTTP_404_NOT_FOUND)

    def get(self, request, activity_id):
        try:
            activity = Activity.objects.get(id=activity_id)
            serializer = ActivitySerializer(activity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Activity.DoesNotExist:
            return Response({'errors': 'Invalid activity_id'},
                            status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, activity_id):
        try:
            activity = Activity.objects.get(id=activity_id)
            activity.delete()
            return Response('', status=status.HTTP_204_NO_CONTENT)
        except Activity.DoesNotExist:
            return Response({'errors': 'Invalid activity_id'},
                            status=status.HTTP_404_NOT_FOUND)


class Registration(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, activity_id):
        try:
            activity = Activity.objects.get(id=activity_id)
            user = request.user
            if user.is_staff or user.is_superuser:
                    return Response({'errors': 'Only students can apply submissions'},
                                    status=status.HTTP_403_FORBIDDEN)
            repo = request.data['repo']

            submission = Submission.objects.create(user_id=user.id, activity_id=activity.id, repo=repo, grade=None)

            serializer = SubmissionSerializer(submission)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response({'errors': f'{str(e)} is missing'})
        except Activity.DoesNotExist:
            return Response({'errors': 'Invalid course_id'},
                            status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'errors': 'Invalid user_id list'},
                            status=status.HTTP_404_NOT_FOUND)

class SubmissionView(APIView):
    permission_classes = [IsAuthenticated, Facilitator]
    authentication_classes = [TokenAuthentication]

    def put(self, request, submission_id):
        try:
            submission = Submission.objects.get(id=submission_id)
            grade = request.data['grade']

            submission.grade = grade
            submission.save()

            serializer = SubmissionSerializer(submission)

            return Response(serializer.data)
        except Submission.DoesNotExist:
            return Response({'errors': 'Invalid submission_id'},
                            status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response({'errors': f'{str(e)} is missing'})


class AllSubmissions(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user

        if not user.is_staff and not user.is_superuser:
            submissions = user.submission_set
            serializer = SubmissionSerializer(submissions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        submissions = Submission.objects.all()
        serializer = SubmissionSerializer(submissions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
