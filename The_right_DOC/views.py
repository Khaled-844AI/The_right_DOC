import json

from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.urls import reverse

from django.utils import timezone
from django.contrib.auth import views as auth_views, logout
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import CreateView

from The_right_DOC.decorators import patient_required, doctor_required
from The_right_DOC.form import Doctor_RegistrationForm, Patient_RegistrationForm, ReservationForm, LoginForm
from The_right_DOC.models import Doctor, Patient, OtpToken, Markers, Reservation, User
from django.contrib.auth.decorators import login_required
from The_right_DOC.form import SPECIALTY_CHOICES

def main_page(request):
    return render(request, 'index.html')


def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()

    if request.method == 'POST':

        # valid token
        if user_otp.otp_code == request.POST['otp_code']:

            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True

                user = User.objects.get(email=user.email)
                user.is_active = True
                user.save()
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("login")

            # expired token
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                patient = Patient.objects.filter(email=username)
                patient.delete()
                return redirect("verify-email", username=user.username)


        # invalid otp code
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            user.is_active = False
            return redirect("verify-email", username=user.username)

    context = {}
    return render(request, "verify_otp.html", context)


def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]

        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))

            # email variables
            subject = "Email Verification"
            message = f"""
                                Hi {user.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{user.username}

                                """
            sender = "mouadkhaled2004@gmail.com"
            receiver = [user.email, ]

            # send email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )

            messages.success(request, "A new OTP has been sent to your email-address")
            storage = messages.get_messages(request)
            storage.used = True
            return redirect("verify-email", username=user.username)

        else:

            messages.error(request, "This email dosen't exist in the database")
            storage = messages.get_messages(request)
            storage.used = True
            return redirect("/register")

    context = {}
    return render(request, "resend_otp.html", context)




class PatientSignUpView(CreateView):
    model = User
    form_class = Patient_RegistrationForm
    template_name = 'Patient_R.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'patient'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save(self.request)
        messages.success(self.request, f"You account has been successfully created please check {user.email}")
        storage = messages.get_messages(self.request)
        storage.used = True
        login(self.request, user)
        return redirect('login')


class DoctorSignUpView(CreateView):
    model = User
    form_class = Doctor_RegistrationForm
    template_name = 'Doctor_R.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'doctor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"You account has been successfully created please check {user.email}"
                                       f"and wait for approval")
        storage = messages.get_messages(self.request)
        storage.used = True
        return redirect('login')


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'Signin.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            user.is_patient = True
        if user.is_authenticated:
            print(user.is_patient)
            print(user.is_doctor)
            if user.is_patient:
                print('patient')
                return reverse('map')
            elif user.is_doctor:
                doctor = Doctor.objects.get(username=user.username)
                if not doctor.accepted:
                    messages.error(self.request, f"Account not approved yet wait for approval")
                    storage = messages.get_messages(self.request)
                    storage.used = True
                    return reverse('login')
                else:
                    print('doctor')
                    return reverse('doctor-profile', kwargs={'pk': user.username})
        return reverse('login')

    def form_invalid(self, form):
        # Add a message for invalid login (incorrect username or password)
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


def choose(request):
    return render(request, "patient_or_doc.html")


@doctor_required(login_url='/login')
def doctor_reservation(request, full_name):
    form = ReservationForm()

    return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                               "full_name": full_name})


@patient_required(login_url='/login')
def map(request):
    markers = Markers.objects.all().values('doctor__username', 'doctor__specialty', 'doctor__price','doctor__start_w',
                                           'doctor__end_w','latitude', 'longitude', 'description')
    # Pass the marker data to the template
    return render(request, 'map.html', {'markers': markers, 'SPECIALTY_CHOICES': [specialty[0] for specialty in SPECIALTY_CHOICES]})


@patient_required(login_url='url')
def make_reservation(request):
    form = ReservationForm()
    full_name = request.POST['full_name']
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            date = request.POST['reservation_date']  # Assuming your form field name is 'reservation_date'

            description = form.cleaned_data['description']
            patient = request.user
            print(full_name + date + description)
            doctor = Doctor.objects.get(username=full_name)


            # Check if a reservation already exists for this doctor, patient, and date
            if Reservation.objects.filter(doctor=doctor, patient=patient, date=date).exists():
                messages.error(request, f'You already did a reservation with Dr {doctor}')
                storage = messages.get_messages(request)
                storage.used = True
                return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                                           "full_name": full_name})
            # Get the highest priority reservation for this doctor and date
            highest_priority = Reservation.objects.filter(doctor=doctor, date=date).order_by('-priority').first()

            # Check if the maximum reservations per day limit is reached for the doctor
            if highest_priority and highest_priority.priority >= doctor.max_pat_day:
                messages.error(request, 'Maximum reservations reached today')
                storage = messages.get_messages(request)
                storage.used = True
                return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                                           "full_name": full_name})

            # Create a new reservation instance and save it
            reservation = Reservation(doctor=doctor, patient=patient, date=date, description=description)
            reservation.save()

            messages.success(request, f'Reservation at {date} been successfully created')
            storage = messages.get_messages(request)
            storage.used = True
            return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                                       "full_name": full_name})
        else:
            messages.error(request, 'Invalid form')
            storage = messages.get_messages(request)
            storage.used = True
    return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                               "full_name": full_name})


@doctor_required(login_url='url')
def doctor_profile(request , pk):
    doctor = Doctor.objects.get(username=pk)
    print(request.user.username)
    if request.user.username == doctor.username:
        if request.method == 'POST':
            start_w = request.POST.get('start_w')
            end_w = request.POST.get('end_w')
            max_pat_day = request.POST.get('max_pat_day')
            none_work = request.POST.getlist('none_work[]')

            print(start_w)

            doctor.start_w = start_w
            doctor.end_w = end_w
            doctor.max_pat_day = max_pat_day
            doctor.none_work = ",".join(none_work)
            doctor.save()
            messages.success(request, 'Your information has been successfully updated.')
            return redirect('doctor-profile', pk=pk)

    context = {'doctor': doctor}
    return render(request, "Doctor_Dashboard/Doctor_prof.html", context)


def logoutUser(request):
    logout(request)
    return redirect('main-page')

