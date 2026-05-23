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
def login(request):
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
def register(request):
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


def competition_list(request):
    c_type = request.GET.get('type', '')
    c_status = request.GET.get('status', '')
    competitions = models.Competition.objects.all()
    if c_type:
        competitions = competitions.filter(type=c_type)
    if c_status:
        competitions = competitions.filter(status=c_status)
    competitions = competitions.order_by('-created_at')
    data = []
    for c in competitions:
        data.append({
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "location": c.location,
            "description": c.description,
            "type": c.type,
            "status": c.status,
            "max_participants": c.max_participants,
            "current_participants": c.current_participants,
            "reward_points": c.reward_points,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "created_at": c.created_at,
            "organizer": {
                "id": c.organizer.id,
                "username": c.organizer.username,
                "nickname": c.organizer.nickname
            }
        })
    return JsonResponse({"success": True, "competitions": data})


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
def user_detail(request, user_id):
    user = models.User.objects.filter(id=user_id).first()
    data = {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "role": user.role,
        "points": user.points,
        "created_at": user.created_at,
        "is_deleted": user.is_deleted,
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
        invite_code = data.get("invite_code", '').strip()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    player = models.User.objects.filter(id=player_id, role='PLAYER').first()
    if not player:
        return JsonResponse({"success": False, "msg": "用户不存在"})
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"})
    if models.Registration.objects.filter(player=player, competition=competition).exists():
        return JsonResponse({"success": False, "msg": "你已报名该赛事"})

    if competition.type == 'PUBLIC':
        status = 0
        invite_code = ''
    elif competition.type == 'PRIVATE':
        if not invite_code:
            return JsonResponse({"success": False, "msg": "私人赛需要提供邀请码"})
        status = 1
    models.Registration.objects.create(
        player=player,
        competition=competition,
        status=status,
        invite_code=invite_code
    )
    return JsonResponse({"success": True, "msg": "报名成功"})

@csrf_exempt
def create_competition(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        player_id = data.get("player_id")
        competition_id = data.get("competition_id")
        invite_code = data.get("invite_code",'').strip()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    player = models.User.objects.filter(id=player_id, role='PLAYER').first()
    if not player:
        return JsonResponse({"success": False, "msg": "用户不存在"})


    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"})
    if models.Registration.objects.filter(player=player, competition=competition).exists():
        return JsonResponse({"success": False, "msg": "你已报名该赛事"})
    if competition.type == 'PUBLIC':
        status = 0
        invite_code = ''
    elif competition.type == 'PRIVATE':
        if not invite_code:
            return JsonResponse({"success": False, "msg": "私人赛需要提供邀请码"})
        status = 1
    models.Registration.objects.create(
        player=player,
        competition=competition,
        status=status,
        invite_code=invite_code
    )
    return JsonResponse({"success": True, "msg": "报名成功"})

def pending_competitions(request): #管理员查看待审核的赛事
    competitions = models.Competition.objects.filter(type='PUBLIC',status=0).order_by('-created_at')
    data = []
    for c in competitions:
        data.append({
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "location": c.location,
            "description": c.description,
            "max_participants": c.max_participants,
            "current_participants": c.current_participants,
            "reward_points": c.reward_points,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "organizer": {
                "id": c.organizer.id,
                "username": c.organizer.username,
                "nickname": c.organizer.nickname
            }
        })
    return JsonResponse({"success": True,"data": data})

@csrf_exempt
def review_competition(request): #管理员审核赛事 1:通过 4:驳回
    if request.method != "POST":
        return JsonResponse({"success": False,"msg": "仅支持 POST"})
    try:
        data = json.loads(request.body)
        competition_id = data.get("competition_id")
        status = data.get("status")
    except Exception:
        return JsonResponse({"success": False,"msg": "请求格式错误"})
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False,"msg": "赛事不存在"})
    if competition.status != 0:
        return JsonResponse({"success": False,"msg": "该赛事已审核"})
    if status == 1:
        competition.status = 1
    elif status == 4:
        competition.status = 4
    else:
        return JsonResponse({"success": False,"msg": "非法审核状态"})
    competition.save()
    return JsonResponse({"success": True,"msg": "审核完成"})

