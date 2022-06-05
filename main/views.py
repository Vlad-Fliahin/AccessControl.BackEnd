import base64
import io
import datetime
import json
import requests
import cv2
import os
import numpy
import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict, Counter
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from numpy import long
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, action, permission_classes
from .models import *
from .serializers import *
from os import listdir

URL = "https://bank.gov.ua/ua/markets/exchangerates"
BASE_DIR = Path(__file__).resolve().parent.parent
ELECTRICITY_PRICE = 12.41
GAS_PRICE = 3.306
WATER_PRICE = 1.5
MIN_LIVING_PRICE = 300
LIVING_PRICE = 350
PATH = os.getcwd().rsplit('/', 1)[0] + '/media/'


def get_descriptors(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)
    img = numpy.array(img, dtype=numpy.uint8)
    # Threshold
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    # Normalize to 0 and 1 range
    img[img == 255] = 1

    # Harris corners
    harris_corners = cv2.cornerHarris(img, 3, 3, 0.04)
    harris_normalized = cv2.normalize(harris_corners, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32FC1)
    threshold_harris = 125

    # Extract keypoints
    keypoints = []
    for x in range(0, harris_normalized.shape[0]):
        for y in range(0, harris_normalized.shape[1]):
            if harris_normalized[x][y] > threshold_harris:
                keypoints.append(cv2.KeyPoint(y, x, 1))

    # Define descriptor
    orb = cv2.ORB_create()
    # Compute descriptors
    _, des = orb.compute(img, keypoints)
    return keypoints, des


def fingerprint_matcher(db_image_path, input_image_path):
    img1 = cv2.imread(db_image_path, cv2.IMREAD_GRAYSCALE)
    kp1, des1 = get_descriptors(img1)

    img2 = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
    kp2, des2 = get_descriptors(img2)

    # Matching between descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(bf.match(des1, des2), key=lambda match: match.distance)

    distance = 0
    for match in matches:
        distance += match.distance

    # Check fingerprints match
    if len(matches) > 10 and distance < 30:
        print("Fingerprint matches.")
        return True

    print("Fingerprint does not match.")
    return False


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        self.request.user.set_password(self.request.data["password"])
        serializer.save(self.request.user)

    @action(detail=True, methods=['POST'])
    def pay(self, request, user_id=None):
        # check if card
        return JsonResponse({"status": "ok"})

    @action(detail=True, methods=['POST'])
    def has_access(self, request, pk=True):
        room = request.data['room']

        if Access.objects.filter(user=pk, room=room).exists():
            return JsonResponse({"has_access": True})
        return JsonResponse({'has_access': False})

    @action(detail=True, methods=['GET'])
    def get_student_id_if_exists(self, request, pk=None):
        students = Student.objects.all()
        student = -1
        for x in students:
            print(type(pk))
            print(type(x.user_id))
            if int(x.user_id) == int(pk):
                student = int(x.student_id)
            else:
                print(int(x.user_id), pk)
        return JsonResponse({"student_id": student})


@api_view(['POST'])
def verify(request):
    fingerprint = request.data['fingerprint'].encode("ascii")
    fingerprint_bytes = io.BytesIO(base64.b64decode(fingerprint))

    new_path = os.getcwd().rsplit('/', 1)[0] + '/AccessControl/media/input/input_fingerprint.bmp'
    print(new_path)

    pil_image = Image.open(fingerprint_bytes)
    pil_image.save(new_path)

    db_pics_path = os.getcwd().rsplit('/', 1)[0] + '/AccessControl/media/pics/'
    for image in os.listdir(db_pics_path):
        if image[0] == '.':
            continue
        print(image)
        print(db_pics_path + image)
        grant_access = fingerprint_matcher(db_pics_path + image, new_path)
        if grant_access:
            return JsonResponse({'Grant Access': True})
    return JsonResponse({'Grant Access': False})


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [permissions.IsAuthenticated]


class FingerprintViewSet(viewsets.ModelViewSet):
    queryset = Fingerprint.objects.all()
    serializer_class = FingerprintSerializer
    permission_classes = [permissions.IsAuthenticated]


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [permissions.IsAuthenticated]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_statistics(request):
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    d = defaultdict(int)
    for room in Room.objects.all():
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(log_id) FROM main_log "
                           "where main_log.sensor_id in ("
                           "select sensor_id from main_sensor "
                           "where main_sensor.room_id = %(room_id)s) "
                           "and main_log.scan_time between %(start_time)s and %(end_time)s",
                           {'room_id': room.room_id, 'start_time': start_date, 'end_time': end_date})
            logs = cursor.fetchone()[0]
            d[room.description] += logs
    print(d)
    response_data = []
    for key, value in d.items():
        response_data.append({'id': key, 'count': value})
    return JsonResponse(response_data, safe=False)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_backups(request):
    backup_path = BASE_DIR / 'backup'
    backups = listdir(backup_path)
    return JsonResponse(backups, safe=False)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def create_backup(request):
    call_command('dbbackup')
    return JsonResponse({"backup": "True"})


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def restore_database(request):
    file_name = request.data['backup']
    call_command('dbrestore', input_filename=file_name, skip_checks=True, interactive=False)
    return JsonResponse({"restore": "True"})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_living_students_count(request):
    active_users = []
    for user in User.objects.all():
        with connection.cursor() as cursor:
            cursor.execute('select fingerprint_id from main_fingerprint '
                           'where user_id = %(user_id)s',
                           {'user_id': user.id})
            fingerprints = tuple(cursor.fetchall())

            print(fingerprints)

            if fingerprints:
                cursor.execute('select count(log_id) from main_log '
                               'where fingerprint_id in %(user_id)s and '
                               'scan_time >= %(time)s',
                               {'user_id': fingerprints,
                                'time': datetime.datetime.today() - datetime.timedelta(days=3)})
                log_count = cursor.fetchone()[0]
                if log_count > 0:
                    active_users.append(user)
    return JsonResponse({'Living': len(active_users)})


class MeterReadingViewSet(viewsets.ModelViewSet):
    queryset = MeterReading.objects.all()
    serializer_class = MeterReadingSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccessViewSet(viewsets.ModelViewSet):
    queryset = Access.objects.all()
    serializer_class = AccessSerializer
    permission_classes = [permissions.IsAuthenticated]


def convert_to_uah(*args, currency):
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table", id="exchangeRates")

    html_codes = table.findAll(attrs={"data-label": "Код літерний"})
    codes = []
    for code in html_codes:
        local_soup = BeautifulSoup(str(code), 'html.parser')
        codes.append(local_soup.text)

    html_prices = table.findAll(attrs={"data-label": "Офіційний курс"})
    prices = []
    for code in html_prices:
        local_soup = BeautifulSoup(str(code), 'html.parser')
        prices.append(local_soup.text)

    currency_id = codes.index(currency)
    currency_price = float(prices[currency_id].replace(',', '.'))

    data = []
    for val in args:
        data.append(round(val * currency_price, 2))
    return data


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['GET'])
    def get_living_payment(self, request, pk=None):
        with connection.cursor() as cursor:
            cursor.execute("select * from main_meterreading "
                           "where room_id = %(room_id)s "
                           "order by review_date desc",
                           {'room_id': Student.objects.get(pk=pk).room_id})
            data = cursor.fetchall()
            last_month = data[0]
            this_month = data[1]

            # 2 -> water
            # 3 -> electricity
            # 4 -> gas

            electricity_payment = (last_month[3] - this_month[3]) * 2
            gas_payment = (last_month[4] - this_month[4]) * 3
            water_payment = (last_month[2] - this_month[2]) * 5

            locale = request.GET['locale']

            payment_value = MIN_LIVING_PRICE + electricity_payment + gas_payment + water_payment

            if payment_value == 0:
                payment_value = MIN_LIVING_PRICE
            else:
                payment_value += LIVING_PRICE

            if locale == 'ua':
                payment_value = convert_to_uah(payment_value, currency='USD')[0]
                electricity_payment, gas_payment, water_payment = convert_to_uah(electricity_payment, gas_payment,
                                                                                 water_payment, currency='USD')

        return JsonResponse({'electricity': electricity_payment,
                             'gas': gas_payment,
                             'water': water_payment,
                             'payment': payment_value})

    @action(detail=True, methods=['GET'])
    def get_penalty_amount(self, request, pk=None):
        locale = request.GET['locale']
        with connection.cursor() as cursor:
            cursor.execute('select sum(main_fine.value) from main_penalty, main_fine '
                           'where main_fine.fine_id = main_penalty.fine_id and '
                           'main_penalty.student_id = %(student_id)s',
                           {'student_id': pk})
            penalty_amount = cursor.fetchone()[0]
        if locale == 'ua':
            penalty_amount = convert_to_uah(penalty_amount, currency='USD')[0]
        return JsonResponse({'penalty_amount': penalty_amount})


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [permissions.IsAuthenticated]


class PenaltyViewSet(viewsets.ModelViewSet):
    queryset = Penalty.objects.all()
    serializer_class = PenaltySerializer
    permission_classes = [permissions.IsAuthenticated]
