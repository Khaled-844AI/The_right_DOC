from django.urls import path
from The_right_DOC import views

urlpatterns = [
    path('', views.main_page, name='main-page'),
    path('register/doctor/', views.register_doctor, name='register-doctor'),
    path('register/patient/', views.register_patient, name='register-patient'),
    path("verify-email/<slug:username>", views.verify_email, name="verify-email"),
    path("resend-otp", views.resend_otp, name="resend-otp"),
    path("register", views.choose, name="pat-or-doc"),
    path("doctor-reservation/<slug:full_name>", views.doctor_reservation, name="doctor-resevation"),
    path("map", views.map, name="map"),
]
