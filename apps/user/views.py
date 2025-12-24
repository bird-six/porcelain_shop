from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views.generic import FormView
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
from django.conf import settings
from django.core.paginator import Paginator

from io import BytesIO
from PIL import Image
import os
import random

from apps.user.models import User, Notification, Follow
from apps.appreciation.models import Work
from utils.random_name import generate_random_name

def user_register(request):
    """用户注册视图"""
    if request.method == 'POST':
        # 从POST请求中获取表单数据
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        terms_accepted = request.POST.get('terms')

        # 完整性检查
        if not username or not password or not email or not confirm_password or not terms_accepted:
            return render(request, 'user/register_login.html', {'error': '请填写完整信息'})

        # 验证密码是否一致
        if password != confirm_password:
            return render(request, 'user/register_login.html', {'error': '两次输入的密码不一致'})

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return render(request, 'user/register_login.html', {'error': '用户名已存在'})

        # 检查邮箱是否已存在
        if User.objects.filter(email=email).exists():
            return render(request, 'user/register_login.html', {'error': '邮箱已存在'})

        # 生成随机用户名
        name = generate_random_name()

        # 创建新用户
        user = User.objects.create_user(username=username, password=password, name=name, email=email)

        # 为新用户随机分配一个默认头像
        try:
            default_avatars = ['default1.webp', 'default2.webp', 'default3.webp']
            avatar_name = random.choice(default_avatars)
            avatar_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'default_avatars', avatar_name)

            if os.path.exists(avatar_path):
                with open(avatar_path, 'rb') as f:
                    # 保存到用户的 ImageField（会复制到 MEDIA_ROOT/avatars/ 下）
                    user.avatar.save(f"default_avatar_{user.id}.webp", File(f), save=True)
        except Exception:
            # 若默认头像分配失败，不影响注册流程
            pass

        # 自动登录用户
        login(request, user)

        # 重定向到首页
        return redirect('index')
    else:
        return render(request, 'user/register_login.html')



def user_login(request):
    """用户登录视图"""
    if request.method == 'POST':
        # 处理POST请求
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 完整性检查
        if not username or not password:
            return render(request, 'user/register_login.html', {'error': '请填写用户名和密码'})

        # 验证用户名和密码
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # 登录用户
            login(request, user)
            # 重定向到首页
            return redirect('index')
        else:
            return render(request, 'user/register_login.html', {'error': '用户名或密码错误'})
    else:
        return render(request, 'user/register_login.html')

def user_logout(request):
    """用户退出登录视图"""
    # 处理GET请求
    if request.method == 'GET':
        # 退出登录
        logout(request)
        # 重定向到首页
        return redirect('index')
    else:
        # 其他请求不合法
        return JsonResponse({'error': '请求方法不合法'}, status=400)


def profile(request, user_id=None):
    """用户个人中心视图：个人信息 + 我的作品分页列表"""
    if not request.user.is_authenticated:
        # 用户未登录，重定向到登录页面
        return redirect('user:user_login')

    if user_id:
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=404)
    else:
        target_user = request.user
    # 查询当前用户的作品（按创建时间倒序）
    works_qs = (
        Work.objects.filter(user=target_user)
        .select_related('category')
        .prefetch_related('workimage_set')
        .order_by('-created_at')
    )

    # 分页处理，每页 9 条
    page = request.GET.get('page', 1)
    paginator = Paginator(works_qs, 9)
    works_page = paginator.get_page(page)

    # 查询用户的收藏作品（点赞的作品）
    liked_works = (
        Work.objects.filter(like__user=target_user)
        .select_related('user')
        .prefetch_related('workimage_set')
        .order_by('-like__created_at')
    )

    # 检查当前用户是否关注了目标用户
    is_following = False
    if request.user.is_authenticated and request.user.id != target_user.id:
        is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()
    
    context = {
        'user': target_user,
        'works_page': works_page,
        'liked_works': liked_works,
        'is_viewing_self': request.user.is_authenticated and request.user.id == target_user.id,
        'is_following': is_following,
    }
    return render(request, 'user/profile.html', context)


@login_required
def get_notifications(request):
    """获取用户通知列表（AJAX）"""
    notification_type = request.GET.get('type', '')
    page = int(request.GET.get('page', 1))
    per_page = 10
    
    # 获取通知查询集
    notifications_qs = Notification.objects.filter(recipient=request.user)
    
    # 根据类型筛选
    if notification_type and notification_type in ['like', 'comment', 'reply', 'follow', 'system']:
        notifications_qs = notifications_qs.filter(notification_type=notification_type)
    
    # 分页
    paginator = Paginator(notifications_qs, per_page)
    notifications_page = paginator.get_page(page)

    # 构建响应数据
    notifications_data = []
    for notification in notifications_page.object_list:
        notifications_data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'content': notification.content,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': notification.is_read,
            'sender': notification.sender.name if notification.sender else '系统',
            'sender_avatar': notification.sender.avatar.url if notification.sender else '',
            'url': notification.get_absolute_url(),
        })
    return JsonResponse({
        'success': True,
        'notifications': notifications_data,
        'has_next': notifications_page.has_next(),
        'total_unread': notifications_qs.filter(is_read=False).count(),
    })


@login_required
def mark_notification_read(request, notification_id):
    """标记单个通知为已读"""
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': '通知不存在'})


@login_required
def mark_all_notifications_read(request):
    """标记所有通知为已读"""
    try:
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_unread_notifications_count(request):
    """获取未读通知数量"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'success': True, 'count': count})

@login_required
def edit_profile(request):
    """编辑用户个人信息视图（Ajax 提交）"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=405)

    user = request.user

    # 基本信息
    name = request.POST.get('name', '').strip()
    introduction = request.POST.get('introduction', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    location = request.POST.get('location', '').strip()

    if not name:
        return JsonResponse({'success': False, 'error': '昵称不能为空'}, status=400)

    # 头像校验（类型 + 大小 5MB 内）
    avatar_file = request.FILES.get('avatar')
    print(avatar_file)
    if avatar_file:
        valid_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in valid_content_types:
            return JsonResponse({'success': False, 'error': '头像格式不正确，仅支持 JPG、PNG、GIF、WEBP'}, status=400)

        max_size = 5 * 1024 * 1024  # 5MB
        if avatar_file.size > max_size:
            return JsonResponse({'success': False, 'error': '头像文件大小不能超过 5MB'}, status=400)

        # 将头像统一转为 webp 格式保存
        try:
            image = Image.open(avatar_file)
            # webp 不支持部分模式，统一转为 RGB
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            output_io = BytesIO()
            image.save(output_io, format='WEBP', quality=85)
            output_io.seek(0)

            webp_name = f"avatar_{user.id}.webp"
            webp_file = InMemoryUploadedFile(
                output_io,
                field_name='avatar',
                name=webp_name,
                content_type='image/webp',
                size=output_io.getbuffer().nbytes,
                charset=None
            )
            user.avatar = webp_file
        except Exception:
            return JsonResponse({'success': False, 'error': '头像图片处理失败，请更换图片重试'}, status=400)
    # 更新其它字段
    user.name = name
    user.introduction = introduction
    user.email = email
    user.phone = phone
    user.location = location
    user.save()

    return JsonResponse({
        'success': True,
        'message': '个人资料已更新',
        'data': {
            'name': user.name,
            'introduction': user.introduction,
            'email': user.email,
            'phone': user.phone,
            'location': user.location,
            'avatar_url': user.avatar.url if user.avatar else ''
        }
    })


@login_required
def follow_user(request, user_id):
    """关注用户视图（Ajax 提交）"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=405)
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': '用户不存在'}, status=404)
    
    # 检查是否已经关注
    if Follow.objects.filter(follower=request.user, following=target_user).exists():
        return JsonResponse({'success': False, 'error': '已经关注了该用户'}, status=400)
    
    # 检查是否关注自己
    if request.user == target_user:
        return JsonResponse({'success': False, 'error': '不能关注自己'}, status=400)
    
    # 创建关注关系
    Follow.objects.create(follower=request.user, following=target_user)
    
    # 创建关注通知
    Notification.objects.create(
        recipient=target_user,
        sender=request.user,
        notification_type='follow',
        content=f"{request.user.name} 关注了您"
    )
    
    return JsonResponse({
        'success': True,
        'message': '关注成功',
        'following': True
    })


@login_required
def unfollow_user(request, user_id):
    """取消关注用户视图（Ajax 提交）"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持 POST 请求'}, status=405)
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': '用户不存在'}, status=404)
    
    # 检查是否已经关注
    follow = Follow.objects.filter(follower=request.user, following=target_user).first()
    if not follow:
        return JsonResponse({'success': False, 'error': '还没有关注该用户'}, status=400)
    
    # 删除关注关系
    follow.delete()
    
    return JsonResponse({
        'success': True,
        'message': '取消关注成功',
        'following': False
    })