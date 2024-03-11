import secrets
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib import messages

from django.db import models
from django.contrib import messages


class Doctor(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    office_location = models.CharField(max_length=50)
    specialty = models.CharField(unique=True, max_length=20)
    start_w = models.TimeField(default='00:00:00')
    end_w = models.TimeField(default='00:00:00')
    visit_duration = models.TimeField(default='00:00:00')
    graduation_certificate = models.ImageField(upload_to='files/Certificate')
    password = models.CharField(max_length=100, null=False, default='None')
    accepted = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        # Hash the password before saving
        if self.password != 'None':  # Only hash if a password is provided
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def check_duration(self,request):
        if self.start_w >= self.end_w:
            messages.error(request,"Invalid time: Start time must be before end time.")

    def __str__(self):
        return self.full_name


class Markers(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.CharField(max_length=200, default='None')

    def __str__(self):
        return f"Marker - Lat: {self.latitude}, Long: {self.longitude} \n -Description: {self.description}"


class Patient(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    def __str__(self):
        return self.username


class OtpToken(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    tp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username


#class Reservation(models.Model):
#    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
#    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#    date = models.DateField()
#    start_time = models.TimeField()
#    end_time = models.TimeField()

 #   def clean(self):
 #       super().clean()
  #      if Reservation.objects.filter(doctor=self.doctor, date=self.date, start_time__lte=self.end_time, end_time__gte=self.start_time).exists():
   #         raise ValidationError("Doctor is not available at this time.")