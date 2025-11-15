from django.db import models
from django.contrib.auth.models import AbstractUser


'''
字段名	类型 / 说明
username	字符串（唯一），用户登录的唯一标识符（必填），长度不超过 150 字符。
password	字符串，存储加密后的密码（通过哈希算法处理，不存储明文）。
email	字符串，用户的电子邮件地址（可选）。
first_name	字符串，用户的名（可选）。
last_name	字符串，用户的姓（可选）。
is_active	布尔值，标识用户是否 “活跃”（默认True）。禁用用户（设为False）无法登录。
is_staff	布尔值，标识用户是否有权限登录 Django 管理后台（admin）。
is_superuser	布尔值，标识用户是否为 “超级用户”（拥有所有权限，无需单独配置权限）。
date_joined	日期时间，用户注册的时间（自动记录，默认当前时间）。
last_login	日期时间，用户最后一次登录的时间（未登录过则为None）。
'''

'''
方法名	作用
set_password(raw_password)	设置用户密码（自动对明文密码进行哈希处理，避免存储明文）。
check_password(raw_password)	验证输入的明文密码是否与存储的哈希密码匹配（返回True/False）。
get_full_name()	返回用户的全名（first_name + last_name，若未设置则返回空字符串）。
get_short_name()	返回用户的名（first_name）。
is_authenticated	属性（非方法），判断用户是否已认证（登录）。匿名用户返回False。
has_perm(perm)	检查用户是否拥有指定权限（如app_label.permission_code）。
has_module_perms(app_label)	检查用户是否拥有指定应用的所有权限。
'''
class User(AbstractUser):
    name = models.CharField(max_length=8, verbose_name='平台用户名')

    class Meta:
        # 自定义模型在 admin 中的显示名称（可选）
        verbose_name = '用户'
        verbose_name_plural = '用户'