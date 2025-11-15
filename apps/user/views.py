from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import FormView

from apps.user.models import User
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
