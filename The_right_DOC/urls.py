from django.urls import path
from The_right_DOC import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.main_page, name='main-page'),
    path('register/doctor/', views.register_doctor, name='register-doctor'),
    path('register/patient/', views.register_patient, name='register-patient'),
    path("verify-email/<slug:username>", views.verify_email, name="verify-email"),
    path("resend-otp", views.resend_otp, name="resend-otp"),
    path("register", views.choose, name="pat-or-doc"),
    path("doctor-reservation/<slug:full_name>", views.doctor_reservation, name="doctor-reservation"),
    path("reservation", views.make_reservation, name="reservation"),
    path("map", views.map, name="map"),
    path("reset_password", auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
         name="reset_password"),
    path("reset_password_sent", auth_views.PasswordResetDoneView.as_view(template_name="done.html"),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="confirm.html"),
         name="password_reset_confirm"),
    path("reset_password_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="complete.html"),
         name="password_reset_complete"),
]
