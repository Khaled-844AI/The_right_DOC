from django.urls import path
from The_right_DOC import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.main_page, name='main-page'),
    path("register/patient/", views.PatientSignUpView.as_view(), name="register-patient"),
    path("register/doctor/", views.DoctorSignUpView.as_view(), name="register-doctor"),
    path("verify-email/<slug:username>", views.verify_email, name="verify-email"),
    path("login/", views.LoginView.as_view(), name="login"),
    path('logout/', views.logoutUser, name='logout'),
    path("resend-otp", views.resend_otp, name="resend-otp"),
    path("register", views.choose, name="pat-or-doc"),
    path("doctor-reservation/<slug:full_name>", views.doctor_reservation, name="doctor-reservation"),
    path("doctor-profile/<str:pk>", views.doctor_profile, name="doctor-profile"),
    path("doc-list/", views.docListView, name="doc-list"),
    path("reservation/", views.make_reservation, name="reservation"),
    path("appointment/" , views.see_apointement, name="see_appointment"),
    path("statistics/" , views.see_statistics, name="see_statistics"),
    path("my-reservations/", views.check_reservations, name="chk-reservations"),
    path('done_reservation/<int:reservation_id>/', views.decide_reservations, name="done_reservation"),
    path('reservations/cancel/<int:reservation_id>/', views.cancel_reservations, name='cancel_reservation'),
    path("map", views.map, name="map"),
    path("reset_password", auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
         name="reset_password"),
    path("reset_password_sent", auth_views.PasswordResetDoneView.as_view(template_name="done.html"),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="confirm.html"),
         name="password_reset_confirm"),
    path("reset_password_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="complete.html"),
         name="password_reset_complete"),
    path("contact_us", views.contact_us, name="contact-us"),

]
