from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import student, Faculty

class StudentBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            stu = student.objects.get(username=username)
        except student.DoesNotExist:
            return None

        if stu and check_password(password, stu.password):
            return stu
        return None

    def get_user(self, user_id):
        try:
            return student.objects.get(pk=user_id)
        except student.DoesNotExist:
            return None


class FacultyBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            faculty = Faculty.objects.get(username=username)
        except Faculty.DoesNotExist:
            return None

        if faculty and check_password(password, faculty.password):
            return faculty
        return None

    def get_user(self, user_id):
        try:
            return Faculty.objects.get(pk=user_id)
        except Faculty.DoesNotExist:
            return None
