from django.contrib import admin

from apps.appreciation.models import Work, Category, WorkImage, Tag, WorkTag, Like

# Register your models here.
admin.site.register(Work)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(WorkImage)
class WorkImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'work', 'image')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(WorkTag)
class WorkTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'work', 'tag')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'work', 'user', 'created_at')
