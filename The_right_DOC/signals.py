from django.db.models.signals import post_save
from django.dispatch import receiver

from djangoProject3.settings import AUTH_USER_MODEL
from .models import OtpToken
from django.core.mail import send_mail
from django.utils import timezone


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_token(instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
             OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
             instance.is_active = False
             instance.save()

             # email credentials
             otp = OtpToken.objects.filter(user=instance).last()

             subject = "Email Verification"

             if instance.is_patient:
                message = f"""
                                Hi {instance.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{instance.username}

                                """
                sender = "mouadkhaled2004@gmail.com"
                receiver = [instance.email, ]
                send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )
             elif instance.is_doctor:
                 message = f"""
                                                Hi Dr.{instance.username}, here is your OTP {otp.otp_code} 
                                                it expires in 5 minute, use the url below to redirect back to the website
                                                http://127.0.0.1:8000/verify-email/{instance.username}

                                                 """
                 sender = "mouadkhaled2004@gmail.com"
                 receiver = [instance.email, ]

                 send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )
