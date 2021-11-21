from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser


class Card(models.Model):
    card_id = models.BigAutoField(primary_key=True)
    number = models.CharField(max_length=50)
    cvv = models.CharField(max_length=50)
    expansion_date = models.CharField(max_length=50)


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    card = models.ForeignKey(Card,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE,
                             parent_link=True)
    phone_number = PhoneNumberField(max_length=50)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'phone_number']


class Staff(models.Model):
    staff_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                parent_link=True)
    job = models.CharField(max_length=50)


class Fingerprint(models.Model):
    fingerprint_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             parent_link=True)
    data = models.ImageField(upload_to='pics')


class Room(models.Model):
    room_id = models.BigAutoField(primary_key=True)
    description = models.TextField(blank=True)
    floor = models.IntegerField()


class Sensor(models.Model):
    sensor_id = models.BigAutoField(primary_key=True)
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE,
                             parent_link=True)
    description = models.TextField(blank=True)


class Log(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    fingerprint = models.ForeignKey(Fingerprint,
                                    on_delete=models.CASCADE,
                                    parent_link=True)
    sensor = models.ForeignKey(Sensor,
                               on_delete=models.CASCADE,
                               parent_link=True)
    scan_time = models.DateTimeField()


class MeterReading(models.Model):
    meter_reading_id = models.BigAutoField(primary_key=True)
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE,
                             parent_link=True)
    water = models.IntegerField()
    electricity = models.IntegerField()
    gas = models.IntegerField()
    review_date = models.DateField()


class Access(models.Model):
    access_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             parent_link=True)
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE,
                             parent_link=True)


class Student(models.Model):
    student_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                parent_link=True)
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE,
                             parent_link=True)
    course = models.IntegerField()


class Fine(models.Model):
    fine_id = models.BigAutoField(primary_key=True)
    restriction_start_time = models.TimeField()
    restriction_end_time = models.TimeField()
    value = models.IntegerField()


class Penalty(models.Model):
    penalty_id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student,
                                on_delete=models.CASCADE,
                                parent_link=True)
    fine = models.ForeignKey(Fine,
                             on_delete=models.CASCADE,
                             parent_link=True)
    return_time = models.DateTimeField()
