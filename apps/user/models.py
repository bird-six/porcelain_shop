from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone


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
    name = models.CharField(max_length=12, verbose_name='平台用户名')
    introduction = models.TextField(max_length=200, blank=True, null=True, verbose_name='个人简介')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号码')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='所在地')
    # avatar = models.ImageField(upload_to='avatars/', default='default-avatar.png', verbose_name='头像')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='头像')


class Follow(models.Model):
    """关注模型"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name='关注者')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers', verbose_name='被关注者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')
    
    class Meta:
        verbose_name = '关注'
        verbose_name_plural = '关注'
        unique_together = ('follower', 'following')  # 确保一个用户只能关注另一个用户一次
    
    def __str__(self):
        return f"{self.follower.username} 关注了 {self.following.username}"


class Notification(models.Model):
    """通知模型"""
    # 通知类型
    NOTIFICATION_TYPES = (
        ('like', '点赞'),
        ('comment', '评论'),
        ('reply', '回复'),
        ('follow', '关注'),
        ('system', '系统通知'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收者')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications', verbose_name='发送者')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    content = models.TextField(verbose_name='通知内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # 关联对象（使用通用外键或单独字段）
    work_id = models.IntegerField(null=True, blank=True, verbose_name='作品ID')
    comment_id = models.IntegerField(null=True, blank=True, verbose_name='评论ID')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']  # 按创建时间倒序排列
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.content[:20]}..."
    
    def get_absolute_url(self):
        """获取通知对应的详情页URL"""
        if self.notification_type in ['like', 'comment', 'reply'] and self.work_id:
            return reverse('appreciation:appreciation_detail', kwargs={'pk': self.work_id})
        elif self.notification_type == 'follow':
            return reverse('user:profile', kwargs={'user_id': self.sender.id})
        return reverse('user:profile')  # 默认返回个人中心
