from datetime import datetime, timedelta

from django import forms
from django_recaptcha.fields import ReCaptchaField

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.shortcuts import redirect

from The_right_DOC.models import Doctor, Markers, Reservation, Patient
from django.contrib import messages

SPECIALTY_CHOICES = [
    ("Anatomie pathologique", "Anatomie pathologique"),
    ("Anesthésie-réanimation", "Anesthésie-réanimation"),
    ("Biochimie", "Biochimie"),
    ("Biologie clinique", "Biologie clinique"),
    ("Cardiologie", "Cardiologie"),
    ("Chirurgie générale", "Chirurgie générale"),
    ("Chirurgie orthopédique", "Chirurgie orthopédique"),
    ("Chirurgie pédiatrique", "Chirurgie pédiatrique"),
    ("Chirurgie urologique", "Chirurgie urologique"),
    ("Chirurgie maxillo-faciale", "Chirurgie maxillo-faciale"),
    ("Chirurgie cardio-vasculaire", "Chirurgie cardio-vasculaire"),
    ("Dermatologie", "Dermatologie"),
    ("Endocrinologie – Diabétologie", "Endocrinologie – Diabétologie"),
    ("Gastro-entérologie", "Gastro-entérologie"),
    ("Gynéco-Obstétrique", "Gynéco-Obstétrique"),
    ("Hématologie", "Hématologie"),
    ("Hémobiologie", "Hémobiologie"),
    ("Histo-embryologie", "Histo-embryologie"),
    ("Immunologie", "Immunologie"),
    ("Maladies infectieuses", "Maladies infectieuses"),
    ("Médecine interne", "Médecine interne"),
    ("Médecine légale", "Médecine légale"),
    ("Médecine nucléaire", "Médecine nucléaire"),
    ("Médecine du travail", "Médecine du travail"),
    ("Microbiologie", "Microbiologie"),
    ("Néphrologie", "Néphrologie"),
    ("Neurochirurgie", "Neurochirurgie"),
    ("Neurologie", "Neurologie"),
    ("O.R.L.", "O.R.L."),
    ("Ophtalmologie", "Ophtalmologie"),
    ("Oncologie médicale", "Oncologie médicale"),
    ("Parasitologie", "Parasitologie"),
    ("Pédiatrie", "Pédiatrie"),
    ("Pharmacologie clinique", "Pharmacologie clinique"),
    ("Physiologie", "Physiologie"),
    ("Pneumo-phtisiologie", "Pneumo-phtisiologie"),
    ("Psychiatrie", "Psychiatrie"),
    ("Radiologie - imagerie", "Radiologie - imagerie"),
    ("Radiothérapie", "Radiothérapie"),
    ("Rééducation fonctionnelle", "Rééducation fonctionnelle"),
    ("Rhumatologie", "Rhumatologie")
]

from django import forms
from django.contrib import messages

AVAILABLE_TIMES = [
    ('05:00', '05:00'),
    ('05:30', '05:30'),
    ('06:00', '06:00'),
    ('06:30', '06:30'),
    ('07:00', '07:00'),
    ('07:30', '07:30'),
    ('08:00', '08:00'),
    ('08:30', '08:30'),
    ('09:00', '09:00'),
    ('09:30', '09:30'),
    ('10:00', '10:00'),
    ('10:30', '10:30'),
    ('11:00', '11:00'),
    ('11:30', '11:30'),
    ('12:00', '12:00'),
    ('12:30', '12:30'),
    ('13:00', '13:00'),
    ('13:30', '13:30'),
    ('14:00', '14:00'),
    ('14:30', '14:30'),
    ('15:00', '15:00'),
    ('15:30', '15:30'),
    ('16:00', '16:00'),
    ('16:30', '16:30'),
    ('17:00', '17:00'),
    ('17:30', '17:30'),
    ('18:00', '18:00'),
    ('18:30', '18:30'),
    ('19:00', '19:00')
]


RESERVATION_TIMES = []


class Doctor_timingForm(forms.Form):
    start_w = forms.ChoiceField(choices=AVAILABLE_TIMES, widget=forms.Select(attrs={
        'class': 'select',
        'placeholder': 'start at',
        'required': 'True'
    }))

    end_w = forms.ChoiceField(choices=AVAILABLE_TIMES, widget=forms.Select(attrs={
        'class': 'select',
        'placeholder': 'finish at',
        'required': 'True'
    }))


    def check_duration(self, request):
        start = self.cleaned_data.get('start_w')
        end = self.cleaned_data.get('end_w')

        s_hour, s_min = start.split(":")
        e_hour, e_min = end.split(":")

        if int(s_hour) > int(e_hour) or int(s_hour) == int(e_hour):
            messages.error(request, "Invalid time")  # Corrected this line

    def save(self, doctor):
        doctor.start_w = self.start_w
        doctor.end_w = self.end_w
        doctor.save()

        return doctor


class ReservationForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'popup-date',
        'placeholder': 'Describe your situation',
        'required': 'True'
    }))


User = get_user_model()

class Doctor_RegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Your email',
        'required': 'True'
    }))
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Your name',
        'required': 'True'
    }))
    specialty = forms.ChoiceField(choices=SPECIALTY_CHOICES, widget=forms.Select(attrs={
        'class': 'select',
        'placeholder': 'Select Specialty',
        'required': 'True'
    }))
    office_location = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Your office location',
        'required': 'True'
    }))
    graduation_certificate = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'input',
        'placeholder': 'Certificate',
        'required': 'True'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input',
        'placeholder': 'Your password',
        'required': 'True'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input',
        'placeholder': 'Re-enter your password',
        'required': 'True'
    }))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'full_name', 'password1', 'password2')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Doctor.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if Doctor.objects.filter(username=full_name).exists():
            raise forms.ValidationError('this username already exists')
        return full_name

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['full_name']
        user.is_doctor = True
        if commit:
            user.save()
        doctor = Doctor.objects.create(user=user, username=self.cleaned_data['full_name'],
            email=self.cleaned_data['email'],
            office_location=self.cleaned_data['office_location'],
            specialty=self.cleaned_data['specialty'],
            graduation_certificate=self.cleaned_data['graduation_certificate'],
            password=self.cleaned_data['password1'])
        marker = Markers.objects.create(
            doctor=doctor,
            latitude=12,
            longitude=-15,
            description=f'-Doctor: {doctor.username} \n-Specialty: {doctor.specialty}'
        )
        marker.save()
        return user


class Patient_RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Your name',
        'required': 'True'
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Your email',
        'required': 'True'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input',
        'placeholder': 'Your password',
        'required': 'True'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input',
        'placeholder': 'Re-enter your password',
        'required': 'True'
    }))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    @transaction.atomic
    def save(self, request, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        if User.objects.filter(email=email, is_active=True).exists():
            messages.error(request, 'Email is already in use.')
            return redirect('register-patient')
        user.is_patient = True
        if commit:
            user.save()
        patient = Patient.objects.create(user=user, email=self.cleaned_data['email'],
                                         is_active=False)
        return user



class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField()
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Your username',
        'required': 'True'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input',
        'placeholder': 'Your password',
        'required': 'True'
    }))
