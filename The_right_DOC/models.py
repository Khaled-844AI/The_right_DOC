import secrets
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Doctor_S_up(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    office_location = models.CharField(max_length=50)
    specialty = models.CharField(unique=True, max_length=20)
    graduation_certificate = models.ImageField(upload_to='files/Certificate')
    password = models.CharField(max_length=100, null=False, default='None')
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Markers(models.Model):
    doctor = models.ForeignKey(Doctor_S_up, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.CharField(max_length=200, default='None')

    def __str__(self):
        return f"Marker - Lat: {self.latitude}, Long: {self.longitude} \n -Description: {self.description}"


class Patient_S_up(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    def __str__(self):
        return self.username


class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    tp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
