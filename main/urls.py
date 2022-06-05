from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import include, path

router = DefaultRouter()
router.register('user', UserViewSet)
router.register('staff', StaffViewSet)
router.register('sensor', SensorViewSet)
router.register('fingerprint', FingerprintViewSet)
router.register('log', LogViewSet)
router.register('room', RoomViewSet)
router.register('meter-reading', MeterReadingViewSet)
router.register('access', AccessViewSet)
router.register('student', StudentViewSet)
router.register('fine', FineViewSet)
router.register('penalty', PenaltyViewSet)

urlpatterns = [
    path('verify/', verify),
    # path('has-access/', has_access),
    path('get-statistics/', get_statistics),
    path('get-living-students-count/', get_living_students_count),
    path('get-backups/', get_backups),
    path('backup/', create_backup),
    path('restore/', restore_database),
    path('', include(router.urls)),
]
