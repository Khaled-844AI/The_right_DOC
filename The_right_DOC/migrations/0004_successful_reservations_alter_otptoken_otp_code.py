# Generated by Django 4.2.9 on 2024-04-16 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('The_right_DOC', '0003_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Successful_reservations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('num_patients', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='4f34d7', max_length=6),
        ),
    ]
