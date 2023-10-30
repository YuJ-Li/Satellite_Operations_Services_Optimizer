from django.urls import path
from . import views

urlpatterns = [
    path('',views.getData),
    path('satellites/', views.satellite_list),
    path('satellites/<str:satellite_id>/', views.satellite_detail, name='satellite_detail'),
    path('satelliteSchedules/', views.satellite_schedule_list),
    path('satelliteSchedules/<str:schedule_id>/', views.satellite_schedule_detail, name='satellite_schedule_detail'),
    path('imaingTasks/', views.imaging_task_list),
    path('imaingTasks/<str:task_id>/', views.imaging_task_detail, name='imaging_task_detail'),
    path('downlinkTasks/', views.downlink_task_list),
    path('downlinkTasks/<str:task_id>/', views.downlink_task_detail, name='downlink_task_detail'),
    path('maintenanceTasks/', views.maintenance_task_list),
    path('maintenanceTasks/<str:task_id>/', views.maintenance_task_detail, name='maintenance_detail'),
    path('groundStations/', views.ground_station_list),
    path('groundStations/<str:station_id>/', views.ground_station_detail, name='groundStation_detail'),
    path('groundStationRequests/', views.ground_station_request_list),
    path('groundStationRequests/<str:stationRequest_id>/', views.ground_station_request_detail, name='groundStationRequest_detail'),
    path('images/', views.image_list),
    path('images/<str:image_id>/', views.image_detail, name='image_detail'),
    path('outages/', views.outage_list),
    path('outages/<str:outage_id>/', views.outage_detail, name='outage_detail'),
]