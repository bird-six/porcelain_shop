from django.urls import path
from apps.master import views

urlpatterns = [
    path('', views.master, name='master'),
]