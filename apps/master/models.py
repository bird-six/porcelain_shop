# from django.db import models
# from django.conf import settings
# from apps.appreciation.models import Work
#
# # 大师头衔
# MASTER_TITLE = (
#     ('国家级大师', '国家级大师'),
#     ('省级大师', '省级大师'),
#     ('市级大师', '市级大师'),
#     ('新生代大师', '新生代大师'),
#     ('非遗传承人', '非遗传承人'),
# )
#
# # 大师领域
# MASTER_FIELD = (
#     ('青花瓷', '青花瓷'),
#     ('粉彩瓷', '粉彩瓷'),
#     ('颜色釉', '颜色釉'),
#     ('雕塑瓷', '雕塑瓷'),
#     ('古瓷修复', '古瓷修复'),
#     ('陶瓷雕塑', '陶瓷雕塑'),
#     ('现代陶艺', '现代陶艺'),
#     ('手工制瓷技艺', '手工制瓷技艺'),
#     ('古陶瓷鉴定与仿制', '古陶瓷鉴定与仿制'),
# )
#
#
# class Master(models.Model):
#     """大师模型"""
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='master_profile',
#                                 verbose_name='关联用户')
#     name = models.CharField(max_length=50, verbose_name='姓名')
#     photo = models.ImageField(upload_to='master_photos/', verbose_name='大师照片')
#     avatar = models.ImageField(upload_to='master_avatars/', verbose_name='大师头像')
#     title = models.CharField(max_length=20, choices=MASTER_TITLE, verbose_name='头衔')
#     field = models.CharField(max_length=20, choices=MASTER_FIELD, verbose_name='领域')
#     working_years = models.CharField(max_length=20, verbose_name='从业年限')
#     introduction = models.TextField(verbose_name='大师简介')
#     notable_works_count = models.IntegerField(verbose_name='代表作品数量')
#     awards_count = models.IntegerField(verbose_name='奖项数量')
#     followers_count = models.IntegerField(default=0, verbose_name='粉丝数量')
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
#
#     class Meta:
#         verbose_name = '大师'
#         verbose_name_plural = '大师'
#         ordering = ['-id']
#
#     def __str__(self):
#         return self.name
#
#
# class MasterAchievement(models.Model):
#     """大师成就模型"""
#     master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='achievements', verbose_name='大师')
#     year = models.IntegerField(verbose_name='年份')
#     description = models.CharField(max_length=200, verbose_name='成就描述')
#
#     class Meta:
#         verbose_name = '大师成就'
#         verbose_name_plural = '大师成就'
#         ordering = ['-year']
#
#
# class MasterStudio(models.Model):
#     """大师工作室模型"""
#     master = models.OneToOneField(Master, on_delete=models.CASCADE, related_name='studio', verbose_name='大师')
#     name = models.CharField(max_length=100, verbose_name='工作室名称')
#     photo = models.ImageField(upload_to='studio_photos/', verbose_name='工作室照片')
#     address = models.CharField(max_length=200, verbose_name='工作室地址')
#     opening_hours = models.CharField(max_length=100, verbose_name='开放时间')
#     phone = models.CharField(max_length=20, verbose_name='联系电话')
#
#     class Meta:
#         verbose_name = '大师工作室'
#         verbose_name_plural = '大师工作室'
#
#     def __str__(self):
#         return f"{self.master.name}的工作室"
#
#
# class MasterCourse(models.Model):
#     """大师课程/讲座模型"""
#     master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='courses', verbose_name='大师')
#     title = models.CharField(max_length=100, verbose_name='课程/讲座标题')
#     description = models.CharField(max_length=200, verbose_name='课程/讲座描述')
#     date_time = models.DateTimeField(verbose_name='时间')
#     location = models.CharField(max_length=200, verbose_name='地点')
#     quota = models.IntegerField(verbose_name='名额')
#     registered_count = models.IntegerField(default=0, verbose_name='已报名人数')
#
#     class Meta:
#         verbose_name = '大师课程'
#         verbose_name_plural = '大师课程'
#         ordering = ['date_time']
#
#     def __str__(self):
#         return f"{self.master.name} - {self.title}"
#
#
# class MasterWork(models.Model):
#     """大师动态模型"""
#     master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='representative_works',
#                                verbose_name='大师')
#     work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='master_relations', verbose_name='作品')
#     is_representative = models.BooleanField(default=True, verbose_name='是否为代表作品')
#
#     class Meta:
#         verbose_name = '大师作品'
#         verbose_name_plural = '大师作品'
#
#     def __str__(self):
#         return f"{self.master.name} - {self.work.title}"
#
#
# class RepresentativeWork(models.Model):
#     """大师代表作品模型"""
#     master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='representative_works',
#                                verbose_name='大师')
#     is_representative = models.BooleanField(default=True, verbose_name='是否为代表作品')
#     description = models.TextField(blank=True, verbose_name='代表性描述', help_text='描述该作品作为代表作品的特点或意义')
#     creation_year = models.IntegerField(blank=True, null=True, verbose_name='创作年份')
#
#     class Meta:
#         verbose_name = '大师代表作品'
#         verbose_name_plural = '大师代表作品'
#         ordering = ['order', '-created_at']
#
#     def __str__(self):
#         return f"{self.master.name} - {self.work.title}"