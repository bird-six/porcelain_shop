from django.urls import path
from apps.appreciation import views

urlpatterns = [
    path('', views.appreciation, name='appreciation'),

]
