from django.contrib.auth.models import User
from django.db import models


class Activity(models.Model):
    title = models.CharField(max_length=255, unique=True)
    points = models.IntegerField()

    submissions = models.ManyToManyField(User, related_name='activities', through='activities.Submission')


class Submission(models.Model):
    grade = models.IntegerField(null=True)
    repo = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
