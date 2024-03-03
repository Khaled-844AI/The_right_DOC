from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from The_right_DOC.models import Doctor_S_up, Patient_S_up, Markers


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
        if Doctor_S_up.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def save(self, commit=True):
        doctor = Doctor_S_up(
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

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Patient_S_up.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def save(self, commit=True):
        user = Patient_S_up(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=make_password(self.cleaned_data['password1'])
        )
        if commit:
            user.save()
        return user
