from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls'), name='index'),
    path('user/', include('apps.user.urls', namespace='user')),
    path('appreciation/', include('apps.appreciation.urls', namespace='appreciation')),

    path('master/', include('apps.master.urls', namespace='master')),



    path('test/', core_views.test, name='test'),
]

# 在开发环境中添加静态文件和媒体文件URL支持
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
