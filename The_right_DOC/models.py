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
    full_name = models.CharField(unique=True, max_length=50)
    email = models.EmailField(unique=True)
    office_location = models.CharField(max_length=50)
    specialty = models.CharField( max_length=20)
    start_w = models.TimeField(default='00:00:00')
    end_w = models.TimeField(default='00:00:00')
    graduation_certificate = models.ImageField(upload_to='files/Certificate')
    password = models.CharField(max_length=120, null=False, default='None')
    accepted = models.BooleanField(default=False)
    price = models.IntegerField(default=0)
    max_pat_day = models.IntegerField(default=0)
    none_work = models.CharField(max_length=10)

    def check_duration(self, request):
        if self.start_w >= self.end_w:
            messages.error(request, "Invalid time: Start time must be before end time.")
            raise ValidationError('Invalid time: Start time must be before end time.')

    def __str__(self):
        return self.full_name


class Markers(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.CharField(max_length=200, null=True, blank=True)

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


class Reservation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=150 , default='None')
    priority = models.IntegerField(default=1)

    def set_date(self, date):
        self.date = date

    def save(self, *args, **kwargs):
        if not self.pk:  # If the instance is new
            if Reservation.objects.filter(doctor=self.doctor, patient=self.patient, date=self.date).exists():
                raise ValidationError('You already did a reservation')

            highest_priority = Reservation.objects.filter(doctor=self.doctor, date=self.date).order_by('-priority').first()
            if highest_priority and highest_priority.priority >= self.doctor.max_pat_day:
                raise ValidationError('Maximum reservations reached for today no more patients')
            if highest_priority:
                self.priority = highest_priority.priority + 1
            else:
                self.priority = 1
        super(Reservation, self).save(*args, **kwargs)

