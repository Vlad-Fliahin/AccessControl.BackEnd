import io
import datetime
import json
from pathlib import Path
from collections import defaultdict, Counter
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, action, permission_classes
from .models import *
from .serializers import *
from os import listdir

BASE_DIR = Path(__file__).resolve().parent.parent
ELECTRICITY_PRICE = 12.41
GAS_PRICE = 3.306
WATER_PRICE = 1.5

MIN_LIVING_PRICE = 300
LIVING_PRICE = 350


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


# def verify(request, fingerprint):
#     f = io.BytesIO(base64.b64decode(fingerprint))
#     pilimage = Image.open(f)
#
#     print(os.getcwd())
#     path = os.getcwd() + '/media/pics/'
#
#     pilimage.save(f"{path}test.BMP")
#
#     if True is False:
#         return JsonResponse({})
#     return JsonResponse({})


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
@permission_classes([permissions.AllowAny])
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
                               {'user_id': fingerprints, 'time': datetime.datetime.today() - datetime.timedelta(days=3)})
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

            payment_value = MIN_LIVING_PRICE + electricity_payment + gas_payment + water_payment

            if payment_value == 0:
                payment_value = MIN_LIVING_PRICE
            else:
                payment_value += LIVING_PRICE
        return JsonResponse({'electricity': electricity_payment,
                             'gas': gas_payment,
                             'water': water_payment,
                             'payment': payment_value})

    @action(detail=True, methods=['GET'])
    def get_penalty_amount(self, request, pk=None):
        with connection.cursor() as cursor:
            cursor.execute('select sum(main_fine.value) from main_penalty, main_fine '
                           'where main_fine.fine_id = main_penalty.fine_id and '
                           'main_penalty.student_id = %(student_id)s',
                           {'student_id': pk})
            penalty_amount = cursor.fetchone()[0]
        return JsonResponse({'penalty_amount': penalty_amount})


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [permissions.IsAuthenticated]


class PenaltyViewSet(viewsets.ModelViewSet):
    queryset = Penalty.objects.all()
    serializer_class = PenaltySerializer
    permission_classes = [permissions.IsAuthenticated]
