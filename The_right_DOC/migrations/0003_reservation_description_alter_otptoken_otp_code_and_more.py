# Generated by Django 4.2.9 on 2024-03-16 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('The_right_DOC', '0002_alter_otptoken_otp_code_alter_reservation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='description',
            field=models.CharField(default='None', max_length=150),
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='e37f9f', max_length=6),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='date',
            field=models.DateField(),
        ),
    ]
