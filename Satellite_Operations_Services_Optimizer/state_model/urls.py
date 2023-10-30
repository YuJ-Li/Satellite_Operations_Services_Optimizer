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
    path('maintenanceTasks/<str:task_id>/', views.maintenance_task_detail, name='maintenance_task_detail'),
]