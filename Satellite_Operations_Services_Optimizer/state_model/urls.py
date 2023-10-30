from django.urls import path
from . import views

urlpatterns = [
    path('',views.getData),
    path('satellites/', views.satellite_list),
    path('satelliteSchedules/', views.satellite_schedule_list),
    path('satellites/<str:satellite_id>/', views.satellite_detail, name='satellite_detail'),
    path('satelliteSchedules/<str:schedule_id>/', views.satellite_schedule_detail, name='satellite_schedule_detail'),
]