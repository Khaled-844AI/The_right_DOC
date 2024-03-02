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


admin.site.register(Doctor_S_up)
admin.site.register(OtpToken, OtpTokenAdmin)
admin.site.register(Patient_S_up, Patient_Admin)
admin.site.register(Markers, MarkersAdmin)
