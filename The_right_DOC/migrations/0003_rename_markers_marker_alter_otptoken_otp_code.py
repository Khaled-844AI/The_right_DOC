# Generated by Django 4.2.9 on 2024-05-26 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('The_right_DOC', '0002_alter_markers_doctor_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Markers',
            new_name='Marker',
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='795fd7', max_length=6),
        ),
    ]
