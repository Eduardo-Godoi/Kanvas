from django.urls import path

from .views import CourseViewById, RegisterCourse, Registration

urlpatterns = [
    path('courses/', RegisterCourse.as_view()),
    path('courses/<str:course_id>/', CourseViewById.as_view()),
    path('courses/<str:course_id>/registrations/', Registration.as_view())
]
