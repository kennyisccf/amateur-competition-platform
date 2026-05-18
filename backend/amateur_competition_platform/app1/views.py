from django.http import HttpResponse
from django.shortcuts import render
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