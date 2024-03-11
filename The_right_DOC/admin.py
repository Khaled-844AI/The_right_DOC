from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


# Register your models here.
class Patient_Admin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
         ),
    )


class OtpTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "otp_code")


class MarkersAdmin(admin.ModelAdmin):
    list_display = ("doctor", "latitude", "longitude", "description")


class DoctorAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.check_duration(request)
        super().save_model(request, obj, form, change)


admin.site.register(Doctor, DoctorAdmin)
admin.site.register(OtpToken, OtpTokenAdmin)
admin.site.register(Patient, Patient_Admin)
admin.site.register(Markers, MarkersAdmin)
