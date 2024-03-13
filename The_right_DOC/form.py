from datetime import datetime, timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password

from The_right_DOC.models import Doctor,  Markers , Reservation
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

VISIT_DUR = [
    ('10 min', '10 min'),
    ('20 min', '20 min'),
    ('30 min', '30 min'),
    ('40 min', '40 min'),
    ('50 min', '50 min'),
    ('60 min', '60 min')
]

RESERVATION_TIMES = []


def generate_reservation_times(doctor):
    today = datetime.today()  # Get today's date and time

    hour_second_parts1 = [str(doctor.start_w).split(":")[0],
                         str(doctor.start_w).split(":")[1]]  # Split by " : " and take the first and last elements
    result1 = ":".join(hour_second_parts1)
    hour_second_parts2 = [str(doctor.end_w).split(":")[0],
                         str(doctor.end_w).split(":")[1]]  # Split by " : " and take the first and last elements
    result2 = ":".join(hour_second_parts2)

    start_time = datetime.strptime(result1, "%H:%M").time()
    end_time = datetime.strptime(result2, "%H:%M").time()
    visit_duration_timedelta = timedelta(hours=int(str(doctor.visit_duration).split(':')[1]),
                                         minutes=int(str(doctor.visit_duration).split(':')[2]))

    current_time = datetime.combine(today.date(), start_time)
    end_datetime = datetime.combine(today.date(), end_time)

    while current_time <= end_datetime:
        RESERVATION_TIMES.append(current_time.strftime("%H:%M"))
        current_time += visit_duration_timedelta



class ReservationForm(forms.Form):

    start_w = forms.ChoiceField(choices=RESERVATION_TIMES, widget=forms.Select(attrs={
        'class': 'select',
        'placeholder': 'available reservations',
        'required': 'True'
    }))

    def __init__(self, doctor, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)

        generate_reservation_times(doctor)


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

    visit_dur = forms.ChoiceField(choices=VISIT_DUR, widget=forms.Select(attrs={
        'class': 'select',
        'placeholder': 'Select Specialty',
        'required': 'True'
    }))

    def check_duration(self, request):
        start = self.cleaned_data.get('start_w')
        end = self.cleaned_data.get('end_w')

        s_hour, s_min = start.split(":")
        e_hour, e_min = end.split(":")

        if int(s_hour) > int(e_hour) or int(s_hour) == int(e_hour):
            messages.error(request, "Invalid time")  # Corrected this line

    def save(self,doctor):
        doctor.start_w = self.start_w
        doctor.end_w = self.end_w
        doctor.visit_duration = self.visit_dur
        doctor.save()

        return doctor





class Doctor_RegistrationForm(forms.Form):
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
        if Doctor.objects.filter(full_name=full_name).exists():
            raise forms.ValidationError('this username already exists')
        return full_name

    def save(self, commit=True):
        doctor = Doctor(
            full_name=self.cleaned_data['full_name'],
            email=self.cleaned_data['email'],
            office_location=self.cleaned_data['office_location'],
            specialty=self.cleaned_data['specialty'],
            graduation_certificate=self.cleaned_data['graduation_certificate'],
            password=make_password(password=self.cleaned_data['password1']),
        )
        if commit:
            doctor.save()
            marker = Markers.objects.create(
                doctor=doctor,
                latitude=12,
                longitude=-15,
                description=f'-Doctor: {doctor.full_name} \n-Specialty: {doctor.specialty}'
            )
            marker.save()
        return doctor


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

    class Meta:
        model = get_user_model()
        fields = ["email", "username", "password1", "password2"]


