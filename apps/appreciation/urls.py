from django.urls import path
from apps.appreciation import views

app_name = 'appreciation'
urlpatterns = [
    path('', views.appreciation, name='appreciation'),
    path('detail/<int:pk>/', views.appreciation_detail, name='appreciation_detail'),
    # 发布新作品
    path('edit/', views.edit_work, name='edit_work'),
    # 编辑已有作品
    path('edit/<int:pk>/', views.edit_work, name='edit_work_update'),
    # 删除作品
    path('delete/<int:pk>/', views.delete_work, name='delete_work'),
    # 点赞/取消点赞
    path('toggle_like/<int:pk>/', views.toggle_like, name='toggle_like'),
    # 评论相关路由
    path('add_comment/<int:pk>/', views.add_comment, name='add_comment'),
    path('toggle_comment_like/<int:comment_id>/', views.toggle_comment_like, name='toggle_comment_like'),
    path('get_comments/<int:pk>/', views.get_comments, name='get_comments'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]
