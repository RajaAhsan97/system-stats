from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="dashboard-home"),

    path('cpu-percent/', views.cpu_util_per, name="cpu-percent"),

    path('memory-stats/', views.memory, name="memory-stats"),

    path('disk-storage/', views.diskStorage, name="disk-storage"),

    path('battery-status/', views.BatteryStatus, name="battery-status"),

    path('process-detail/', views.Detail, name="process-detail"),

    path('cpu_count/', views.get_cpu_cnt, name="cpu-cnt"),
    path('pid/', views.pid, name="pid"),

    path('network-detail-pg', views.NetworkDetail, name="network-detail"),
    path('network-stats/', views.Network, name="network-stats"),
    path('network-interface-card/', views.NIC, name="network-interface"),
]
