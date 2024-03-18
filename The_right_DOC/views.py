import json

from bs4 import BeautifulSoup
from django.contrib.auth.hashers import check_password, make_password
from django.db.models.signals import post_save
from django.http import JsonResponse
from django.utils import timezone

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from The_right_DOC.form import Doctor_RegistrationForm, Patient_RegistrationForm, ReservationForm
from The_right_DOC.models import Doctor, Patient, OtpToken, Markers, Reservation
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
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("register-patient")

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


def register_doctor(request):
    if request.method == 'POST':
        if 'sign_up' in request.POST:
            form = Doctor_RegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                # Handle form submission and save the doctor registration
                form.save()
                messages.success(request, "Account created successfully! Please wait for approval.")
                storage = messages.get_messages(request)
                storage.used = True
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    storage = messages.get_messages(request)
                    storage.used = True
        elif 'sign_in' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('pass1')  # Adjust this according to your form field name
            try:
                user = Doctor.objects.get(email=email)
                if check_password(password, user.password):  # Check hashed password
                    if user.accepted:
                        return redirect('/map')
                    else:
                        messages.error(request, "Your account is not yet approved.")
                        storage = messages.get_messages(request)
                        storage.used = True
                else:
                    messages.error(request, "Invalid credentials.")
                    storage = messages.get_messages(request)
                    storage.used = True
            except Doctor.DoesNotExist:
                messages.error(request, "Invalid credentials.")

    form = Doctor_RegistrationForm()
    print("Rendering signup form.")

    return render(
        request=request,
        template_name="Doctor_R.html",
        context={"form": form}
    )


def register_patient(request):
    if request.method == 'POST':
        if 'sign_up' in request.POST:
            form = Patient_RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                print("Form saved successfully.")
                messages.success(request, f'Hy {user.username}, your account has been created successfully.\
                    \nPlease check your email at {user.email} for verification instructions.')
                return redirect('verify-email', username=request.POST['username'])
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    storage = messages.get_messages(request)
                    storage.used = True
        elif 'sign_in' in request.POST:
            email = request.POST.get('email2')
            password = request.POST.get('pass2')
            user = authenticate(request, email=email, password=password)
            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, "Logged In Successfully!!")
                return redirect('/map')
            else:
                messages.error(request, "Bad Credentials!!")
                storage = messages.get_messages(request)
                storage.used = True

    form = Patient_RegistrationForm()
    print("Rendering signup form.")

    return render(
        request=request,
        template_name="Patient_R.html",
        context={"form": form}
    )


def choose(request):
    return render(request, "patient_or_doc.html")


@login_required(login_url='/register')
def doctor_reservation(request, full_name):
    form = ReservationForm()

    return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                               "full_name": full_name})


@login_required(login_url='/register')
def map(request):
    markers = Markers.objects.all().values('doctor__full_name', 'doctor__specialty', 'doctor__price',
                                           'latitude', 'longitude', 'description')
    # Pass the marker data to the template
    return render(request, 'map.html', {'markers': markers, 'SPECIALTY_CHOICES': [specialty[0] for specialty in SPECIALTY_CHOICES]})


@login_required(login_url='/register')
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
            doctor = Doctor.objects.get(full_name=full_name)


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







