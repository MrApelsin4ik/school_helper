from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    full_name = models.CharField(max_length=255)
    whoami = models.IntegerField()

    class Meta:
        app_label = 'school_app'  # Явно указываем, что модель находится в приложении 'school_app'


class Code(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code_end_h = models.IntegerField()
    code_end_m = models.IntegerField()
    code_end_time_in_sec = models.IntegerField()
    code = models.IntegerField()
    code_priority = models.IntegerField()


class Classroom(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    class_number = models.IntegerField()
    class_letter = models.CharField(max_length=1)


class Student(models.Model):
    full_name = models.CharField(max_length=255)
    passport_scan = models.ImageField(upload_to='passport_scans/', blank=True, null=True)
    registration_scan = models.ImageField(upload_to='registration_scans/', blank=True, null=True)
    birth_certificate_scan = models.ImageField(upload_to='birth_certificate_scans/', blank=True, null=True)
    class_number = models.IntegerField()
    class_letter = models.CharField(max_length=1)


class Food_milk(models.Model):
    class_number = models.IntegerField()
    class_letter = models.CharField(max_length=1)
    num_paid = models.IntegerField()
    num_discount = models.IntegerField()
    num_milk = models.IntegerField()
    date = models.DateField()