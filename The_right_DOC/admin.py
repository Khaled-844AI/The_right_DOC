from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


# Register your models here.
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')
    search_fields = ('user__email',)
    list_filter = ('is_active',)


class OtpTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "otp_code")


class MarkersAdmin(admin.ModelAdmin):
    list_display = ("doctor", "latitude", "longitude", "description")


class DoctorAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.check_duration(request)
        super().save_model(request, obj, form, change)


class ReservationAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "date", "priority")

    def save_model(self, request, obj, form, change):
        obj.save()


class Succ_ReservationAdmin(admin.ModelAdmin):
    list_display = ("date", "num_patients")

    def save_model(self, request, obj, form, change):
        obj.save()


admin.site.register(User, BaseUserAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(OtpToken, OtpTokenAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Markers, MarkersAdmin)
admin.site.register(Successful_reservations, Succ_ReservationAdmin)
