from django.urls import path
from apps.master import views

app_name = 'master'
urlpatterns = [
    path('', views.master, name='master'),
    path('customize/', views.customize, name='customize'),
    path('detail/', views.master_detail, name='master_detail'),
]