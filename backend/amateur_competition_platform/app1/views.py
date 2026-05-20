from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from hashlib import md5
from app1 import models

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = models.User.objects.filter(username=username).first()
        if user:
            password_md5 = md5(password.encode()).hexdigest()
            if user.password == password_md5:
                return HttpResponse("登录成功")
            return render(request, "login.html", {"error_msg": "密码错误"})
        else:
            return render(request, "login.html", {"error_msg": "用户不存在"})

    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', '').strip()
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        created_at = datetime.now()
        points = 0
        password_md5 = md5(password.encode()).hexdigest()
        if len(username) > 50:
            return render(request, "register.html", {"error_msg": "用户名不能超过50字符"})
        if len(nickname) > 50:
            return render(request, "register.html", {"error_msg": "昵称不能超过50个字符"})
        if models.User.objects.filter(username = username, is_deleted = False).exists():
            return render(request, "register.html", {"error_msg": "用户名已存在"})
        print(username, password_md5, nickname, created_at, points, role)
        models.User.objects.create(username = username, password = password_md5, nickname = nickname, email = email, points = points, created_at = created_at, role = role)
        return render(request, 'register.html', {"success":True})
    return render(request, 'register.html')

def index(request):
    c_type = request.GET.get('type', '')
    c_status = request.GET.get('status', '')
    competitions = models.Competition.objects.all()
    if c_type:
        competitions = competitions.filter(type=c_type)
    if c_status:
        competitions = competitions.filter(status=c_status)
    competitions = competitions.order_by('-created_at')
    return render(request, 'index.html', {
        'competitions': competitions
    })
