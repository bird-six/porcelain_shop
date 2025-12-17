from django.urls import path
from apps.appreciation import views

app_name = 'appreciation'
urlpatterns = [
    path('', views.appreciation, name='appreciation'),
    path('detail/<int:pk>/', views.appreciation_detail, name='appreciation_detail'),
    path('edit/', views.edit_work, name='edit_work'),

]
