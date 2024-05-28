import calendar
from datetime import datetime

from django.db.models import Q
from django.urls import reverse, reverse_lazy

from django.utils import timezone
from django.contrib.auth import views as auth_views, logout
from django.contrib import messages
from django.contrib.auth import  login, get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import CreateView

from The_right_DOC.decorators import patient_required, doctor_required
from The_right_DOC.form import Doctor_RegistrationForm, Patient_RegistrationForm, ReservationForm, LoginForm, ContactForm
from The_right_DOC.models import Doctor, Patient, OtpToken, Marker, Reservation, User, SuccessfulReservations
from django.contrib.auth.decorators import login_required
from The_right_DOC.form import SPECIALTY_CHOICES
import plotly.express as px


def main_page(request):
    user = request.user

    if user.is_anonymous:
        return render(request, 'index.html', {'user': user, 'doctor': None})

    if user.is_doctor:
       doctor = Doctor.objects.get(username=user.username)
       if doctor:
           return render(request, 'index.html', {'user': user, 'doctor': doctor})
    else:

       return render(request, 'index.html' , {'user': user , 'doctor' : None})


def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()

    if request.method == 'POST':

        # valid token
        if user_otp.otp_code == request.POST['otp_code']:
            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user = User.objects.get(email=user.email)
                user.is_active = True
                user.save()
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
    success_url = reverse_lazy('main-page')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'patient'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save(self.request)
        print(user.is_active)
        messages.success(self.request, f"You account has been successfully created please check {user.email}")
        storage = messages.get_messages(self.request)
        storage.used = True
        return redirect('login')


class DoctorSignUpView(CreateView):
    model = User
    form_class = Doctor_RegistrationForm
    template_name = 'Doctor_R.html'
    success_url = reverse_lazy('main-page')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated :
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'doctor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"You account has been successfully created please check {user.email}"
                                       f" and wait for approval")
        storage = messages.get_messages(self.request)
        storage.used = True
        login(self.request, user)
        return redirect('login')


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'Signin.html'
    success_url = reverse_lazy('main-page')
    failed_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            if request.user.is_patient:
                return redirect(self.success_url)
            if request.user.is_doctor:
                doctor = Doctor.objects.get(username=request.user.username)
                if doctor.accepted:
                    return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            user.is_patient = True
        if user.is_authenticated:
            if user.is_patient:
                return reverse('map')
            elif user.is_doctor:

                try:
                        doctor = Doctor.objects.get(user=user)
                        if doctor.accepted:
                            return reverse('doctor-profile', kwargs={'pk': user.username})
                        else:
                            messages.error(self.request, "Your account is not yet accepted. Please wait for approval.")
                            return reverse('login')
                except Doctor.DoesNotExist:
                        messages.error(self.request, "There is an issue with your doctor account. Please contact support.")
                        return reverse('login')


        return reverse('login')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


def anonymous_required(view_function):
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main-page')
        return view_function(request, *args, **kwargs)

    return wrapped


@anonymous_required
def choose(request):
    return render(request, "patient_or_doc.html")


@patient_required(login_url='/login')
def doctor_reservation(request, full_name):
    form = ReservationForm()
    doctor = Doctor.objects.get(username=full_name)
    return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                               "full_name": full_name,
                                                               "non_work": doctor.none_work})


@login_required(login_url='login')
def map(request):
    markers = Marker.objects.all().values('doctor__username', 'doctor__specialty', 'doctor__price', 'doctor__start_w',
                                           'doctor__end_w', 'latitude', 'longitude', 'description')

    user = request.user

    if request.user.is_doctor:
        doctor = Doctor.objects.get(username=request.user.username)
        return render(request, 'map.html',
                      {'markers': markers, 'SPECIALTY_CHOICES': [specialty[0] for specialty in SPECIALTY_CHOICES],
                       'user': user,
                       'doctor': doctor})


    return render(request, 'map.html',
                  {'markers': markers, 'SPECIALTY_CHOICES': [specialty[0] for specialty in SPECIALTY_CHOICES],
                   'user': user,
                   'doctor':None})


@patient_required(login_url='login')
def make_reservation(request):
    form = ReservationForm()
    full_name = request.POST['full_name']
    doctor = Doctor.objects.get(username=full_name)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            date = request.POST['reservation_date']
            date = str(date)
            print(date)
            description = form.cleaned_data['description']
            patient = Patient.objects.get(user=request.user)

            time = timezone.now().time()
            doc_end_time = doctor.end_w
            print(time)
            print(doc_end_time)
            if time > doc_end_time and date.split('-')[2] == str(timezone.now().day):
                messages.error(request, f'Reservations with Dr {doctor} are done today')
                storage = messages.get_messages(request)
                storage.used = True
                return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                                           "full_name": full_name,
                                                                           "non_work": doctor.none_work})
            # Check if a reservation already exists for this doctor, patient, and date
            if Reservation.objects.filter(doctor=doctor, patient=patient, date=date).exists():
                messages.error(request, f'You already did a reservation with Dr {doctor}')
                storage = messages.get_messages(request)
                storage.used = True
                return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                                           "full_name": full_name,
                                                                           "non_work": doctor.none_work})
            # Get the highest priority reservation for this doctor and date
            highest_priority = Reservation.objects.filter(doctor=doctor, date=date).order_by('-priority').first()

            # Check if the maximum reservations per day limit is reached for the doctor
            if highest_priority and highest_priority.priority >= doctor.max_pat_day:
                messages.error(request, 'Maximum reservations reached today')
                storage = messages.get_messages(request)
                storage.used = True
                return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                                           "full_name": full_name,
                                                                           "non_work": doctor.none_work})

            # Create a new reservation instance and save it
            reservation = Reservation(doctor=doctor, patient=patient, date=date, description=description)
            reservation.save()

            messages.success(request, f'Reservation at {date} been successfully created')
            storage = messages.get_messages(request)
            storage.used = True
            return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                                       "full_name": full_name,
                                                                       "non_work": doctor.none_work})
        else:
            messages.error(request, 'Invalid form')
            storage = messages.get_messages(request)
            storage.used = True
    return render(request, 'Patient_Dashboard/calendar.html', {"form": form,
                                                               "full_name": full_name,
                                                               "non_work": doctor.none_work})


@doctor_required(login_url='login')
def doctor_profile(request, pk):
    doctor = Doctor.objects.get(username=pk)

    if request.user.username == doctor.username:
        if request.method == 'POST':
            start_w = request.POST.get('start_w')
            end_w = request.POST.get('end_w')
            max_pat_day = request.POST.get('max_pat_day')
            none_work = request.POST.getlist('none_work[]')
            price = request.POST.get('price')
            print(price)

            doctor.start_w = start_w
            doctor.end_w = end_w
            doctor.max_pat_day = max_pat_day
            doctor.none_work = ",".join(none_work)
            doctor.price = price
            doctor.save()
            messages.success(request, 'Your information has been successfully updated.')
            return redirect('doctor-profile', pk=pk)

    context = {'doctor': doctor}
    return render(request, "Doctor_Dashboard/Doctor_prof.html", context)


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('main-page')


def docListView(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    doctors = Doctor.objects.filter(
        Q(username__icontains=q) | Q(office_location__icontains=q) | Q(specialty__icontains=q)
    )
    doctors_count = doctors.count()

    if request.user.is_anonymous:
        context = {'doctors': doctors, 'doctors_count': doctors_count, 'doctor': None}

        return render(request, 'doc_list.html', context)

    if request.user.is_doctor:
        doctor = Doctor.objects.get(username=request.user.username)
        context = {'doctors': doctors, 'doctors_count': doctors_count, 'doctor':doctor}

        return render(request, 'doc_list.html', context)

    context = {'doctors': doctors, 'doctors_count': doctors_count, 'doctor': None}
    return render(request, 'doc_list.html', context)


@patient_required(login_url='login')
def check_reservations(request):
    patient = Patient.objects.get(user=request.user)
    current_date = timezone.now().date()  # Get the current date
    # Filter reservations for today and the future
    reservations = Reservation.objects.filter(patient=patient, date__gte=current_date)

    return render(request, 'Patient_Dashboard/Reservation.html', {'reservations': reservations})

@patient_required(login_url='login')
def cancel_reservations(request, reservation_id):
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.delete()
            messages.success(request, 'Reservation canceled successfully.')
        except Reservation.DoesNotExist:
            messages.error(request, 'Reservation not found.')
    return redirect('/my-reservations')  # Redirect to the reservation page



@doctor_required(login_url='login')
def decide_reservations(request, reservation_id):
    if request.method == 'POST':
        if 'submit-button' in request.POST:
            try:
                reservation = Reservation.objects.get(id=reservation_id)
                email = reservation.patient.email

                # Create SuccessfulReservations entry
                res = SuccessfulReservations(doctor=reservation.doctor, date=reservation.date, num_patients=0)
                res.save()

                # Get the next ticket
                reservation.delete()
                next_ticket = reservation.get_highest()

                doctor = Doctor.objects.get(username=request.user.username)

                # Prepare and send email
                sender = "mouadkhaled2004@gmail.com"
                receiver = [email, ]
                subject = "Reservation time!"
                message = f"Hi {reservation.patient.user.username}, time for your reservation with Dr. {doctor.username}."

                send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )

                if next_ticket:
                    messages.success(request, f'Reservation done successfully. Next patient with ticket number {next_ticket}')
                else:
                    messages.error(request, 'No current reservation')
            except Reservation.DoesNotExist:
                messages.error(request, 'Reservation not found.')
        elif 'cancel-button' in request.POST:
            try:
                reservation = Reservation.objects.get(id=reservation_id)
                new_priority = reservation.get_highest()

                date = reservation.date
                doctor = reservation.doctor
                patient = reservation.patient
                description = reservation.description
                reservation.delete()

                if new_priority:
                    Reservation.objects.create(doctor=doctor, patient=patient,
                                               description=description, date=date,
                                               priority=new_priority + 1)
                messages.success(request, 'Reservation canceled successfully.')
                return redirect('see_appointment')
            except Reservation.DoesNotExist:
                messages.error(request, 'Reservation not found.')

    return redirect('/appointment')


@doctor_required(login_url="/login")
def see_apointement(request):
    user = request.user
    doctor = Doctor.objects.get(username=user.username)
    reservations = Reservation.objects.all().order_by('priority')

    if reservations:
        for res in reservations:
            if res.date < timezone.now().date():
                res.delete()

    return render(request,'Doctor_Dashboard/Reservation.html', {'doctor': doctor,
                                                                'reservations': reservations})


@doctor_required(login_url='login')
def see_statistics(request):

    doctor = Doctor.objects.get(username=request.user.username)

    # Get all successful reservations for the current month
    current_date = datetime.now()
    res = SuccessfulReservations.objects.filter(
        doctor=doctor,
        date__year=current_date.year,
        date__month=current_date.month
    )

    days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
    reservations_by_day = {day: 0 for day in range(1, days_in_month + 1)}

    for r in res:
        reservations_by_day[r.date.day] = r.num_patients

    x_values = list(reservations_by_day.keys())  # days per month
    y_values = list(reservations_by_day.values())  # num reservations per day

    fig = px.area(x=x_values,
                  y=y_values,
                  hover_data={'Total earnings': [str(i * doctor.price)+' DA' for i in y_values]},
                  labels={'x': 'Days',
                          'y': 'Patients'
                          })

    fig.update_layout(hoverlabel=dict(bgcolor='green'))

    chart = fig.to_html()

    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    current_month = ''
    for i in range(0, 12):
        if i == current_date.month:
            current_month = months[i - 1]
            break

    return render(request, "Doctor_Dashboard/Statistics.html", {'doctor': doctor, 'chart': chart,
                                                                'month': current_month})

@login_required(login_url='login')
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            # send_mail(
            #     form.cleaned_data['subject'],  # subject
            #     f"Message from {form.cleaned_data['name']} <{form.cleaned_data['email']}>\n\n"
            #     f"{form.cleaned_data['message']}",  # message
            #     None,  # from email
            #     ['5b443ef62d@emailbbox.pro'],  # replace with your email
            # )
            send_mail(
                f"{subject} - {name}",  # Objet de l'email
                f"Email: {email}\n\n{message}",  # Corps de l'email
                email,  # Email de l'expéditeur
                ['7e818481ae@emailbbox.pro'],  # Email du destinataire (support)
                fail_silently=False,  # Gérer les erreurs d'envoi
            )
            return render(request, 'contact_us.html')
    else:
        form = ContactForm()


    if request.user.is_doctor:
        doctor = Doctor.objects.get(username=request.user.username)
        return render(request, 'contact_us.html', {'form': form, 'doctor': doctor})

    return render(request, 'contact_us.html', {'form': form, 'doctor': None})