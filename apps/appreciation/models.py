import os
from django.db import models
from django.conf import settings

# Create your models here.

# 图片上传路径函数
def upload_to_work_images(instance, filename):
    # 保存到media/work_images目录
    return os.path.join('work_images', filename)

class Category(models.Model):
    name = models.CharField(max_length=20)

class Work(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)  # 用户
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # 分类

    title = models.CharField(max_length=20)     # 标题
    description = models.TextField()    # 描述
    material = models.CharField(max_length=20)  # 材质
    technique = models.CharField(max_length=20)  # 工艺
    specification = models.CharField(max_length=20)  # 规格
    origin = models.CharField(max_length=20)  # 产地
    is_salable = models.BooleanField(default=False)  # 是否可售
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 价格

    stock = models.IntegerField(default=0)  # 库存
    views_count = models.IntegerField(default=0)  # 浏览量
    likes_count = models.IntegerField(default=0)  # 点赞量
    comments_count = models.IntegerField(default=0)  # 评论量
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '发布'),
        ('hidden', '隐藏'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')  # 状态

class WorkImage(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_to_work_images)

class Tag(models.Model):
    name = models.CharField(max_length=20)

class WorkTag(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class Like(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

