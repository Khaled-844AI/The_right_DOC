# Generated by Django 4.2.9 on 2024-03-21 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('The_right_DOC', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='full_name',
            new_name='username',
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='976b51', max_length=6),
        ),
    ]
