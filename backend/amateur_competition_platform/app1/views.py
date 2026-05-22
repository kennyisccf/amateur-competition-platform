from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from hashlib import md5
import hashlib
from app1 import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role_map = {"选手": "PLAYER", "主办方": "ORGANIZER", "管理员": "ADMIN"}
        role = role_map.get(data.get("role", "").strip(), "").upper()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if not username or not password or not role:
        return JsonResponse({"success": False, "msg": "用户名、密码或角色不能为空"})
    user = models.User.objects.filter(username=username, role=role).first()
    if not user:
        return JsonResponse({"success": False, "msg": "用户不存在或角色不匹配"})
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    if user.password != password_md5:
        return JsonResponse({"success": False, "msg": "密码错误"})
    return JsonResponse({"success": True, "msg": "登录成功", "user_id": user.id})

# def login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = models.User.objects.filter(username=username).first()
#         if user:
#             password_md5 = md5(password.encode()).hexdigest()
#             if user.password == password_md5:
#                 return HttpResponse("登录成功")
#             return render(request, "login.html", {"error_msg": "密码错误"})
#         else:
#             return render(request, "login.html", {"error_msg": "用户不存在"})
#
#     return render(request, "login.html")
@csrf_exempt
def register_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    password2 = request.POST.get('password2', '').strip()
    role = request.POST.get('role', 'PLAYER').strip().upper()
    nickname = request.POST.get('nickname', username).strip()
    email = request.POST.get('email', '').strip()
    if not username or not password or not password2:
        return JsonResponse({"success": False, "msg": "请填写完整信息"})
    if password != password2:
        return JsonResponse({"success": False, "msg": "两次密码不一致"})
    if len(username) > 50:
        return JsonResponse({"success": False, "msg": "用户名不能超过50字符"})
    if len(nickname) > 50:
        return JsonResponse({"success": False, "msg": "昵称不能超过50个字符"})
    if models.User.objects.filter(username=username, is_deleted=False).exists():
        return JsonResponse({"success": False, "msg": "用户名已存在"})
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    models.User.objects.create(
        username=username,
        password=password_md5,
        nickname=nickname,
        email=email,
        points=0,
        created_at=datetime.now(),
        role=role
    )
    return JsonResponse({"success": True, "msg": "注册成功"})


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


def competition_detail(request, competition_id):
    competition = models.Competition.objects.filter(id=competition_id).first()
    data = {
        "id": competition.id,
        "title": competition.title,
        "category": getattr(competition, "category", ""),
        "location": getattr(competition, "location", ""),
        "description": competition.description,
        "type": competition.type,
        "organizer": {
            "id": competition.organizer.id,
            "username": competition.organizer.username,
            "nickname": competition.organizer.nickname
        },
        "status": competition.status,
        "max_participants": competition.max_participants,
        "current_participants": competition.current_participants,
        "reward_points": getattr(competition, "reward_points", 100),
        "start_time": competition.start_time,
        "end_time": competition.end_time,
        "created_at": competition.created_at
    }
    return JsonResponse({"success": True, "data": data})

@csrf_exempt
def submit_registration(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        player_id = data.get("player_id")
        competition_id = data.get("competition_id")
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    player = models.User.objects.filter(id=player_id, role='PLAYER').first()
    if not player:
        return JsonResponse({"success": False, "msg": "用户不存在"})
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"})
    current_count = models.Registration.objects.filter(competition=competition, status__in=[0,1]).count()
    if current_count >= competition.max_participants:
        return JsonResponse({"success": False, "msg": "报名人数已满"})
    existing = models.Registration.objects.filter(player=player, competition=competition).first()
    if existing:
        return JsonResponse({"success": False, "msg": "你已报名该赛事"})
    models.Registration.objects.create(
        player=player,
        competition=competition,
        status=0,
        final_score='',
        final_rank=0,
        earned_points=0,
        audit_remark=''
    )
    return JsonResponse({"success": True, "msg": "报名成功"})