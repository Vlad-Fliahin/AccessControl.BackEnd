from rest_framework import serializers
from .models import *


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'


class FingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fingerprint
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class MeterReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterReading
        fields = '__all__'


class AccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Access
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = '__all__'


class PenaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = Penalty
        fields = '__all__'
