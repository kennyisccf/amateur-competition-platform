from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from hashlib import md5
import hashlib
from app1 import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import string
import random
from functools import wraps
@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if not username or not password:
        return JsonResponse({"success": False, "msg": "用户名或密码不能为空"})
    user = models.User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({"success": False, "msg": "用户不存在"})
    if user.is_deleted:
        return JsonResponse({"success": False, "msg": "该账号已被封禁"}, status=403)
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    if user.password != password_md5:
        return JsonResponse({"success": False, "msg": "密码错误"})
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    return JsonResponse({"success": True, "msg": "登录成功", "user_id": user.id, "role": user.role})

@csrf_exempt
def logout(request):
    request.session.flush()
    return JsonResponse({"success": True, "msg": "退出登录"})

def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return JsonResponse({"success": False, "msg": "请先登录"}, status=401)
        return func(request, *args, **kwargs)
    return wrapper

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

@csrf_exempt
def competition_list(request):
    c_category = request.GET.get("category", "")
    keyword = request.GET.get("keyword", "")
    competitions = models.Competition.objects.filter(
        status=1
    )
    if c_category:
        competitions = competitions.filter(category__icontains=c_category)
    if keyword:
        competitions = competitions.filter(
            title__icontains=keyword
        )
    competitions = competitions.order_by("-created_at")
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
            "start_time": c.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": c.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "organizer": {
                "id": c.organizer.id,
                "username": c.organizer.username,
                "nickname": c.organizer.nickname
            }
        })
    return JsonResponse({
        "success": True,
        "competitions": data
    })

@csrf_exempt
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
        "reward": competition.reward,
        "start_time": competition.start_time,
        "end_time": competition.end_time,
        "created_at": competition.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return JsonResponse({"success": True, "data": data})

@csrf_exempt
@login_required
def user_detail(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"success": False, "msg": "未登录"})
    user = models.User.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({"success": False,"msg": "用户不存在"})
    data = {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "role": user.role,
        "points": user.points,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "is_deleted": user.is_deleted,
    }
    return JsonResponse({"success": True, "data": data})

@login_required
@csrf_exempt
def update_user(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "请求方式错误"})
    try:
        data = json.loads(request.body)
        user_id = request.session.get("user_id")
        user = models.User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"success": False, "msg": "用户不存在"})
        user.nickname = data.get("nickname", user.nickname)
        user.email = data.get("email", user.email)
        user.save()
        return JsonResponse({"success": True, "msg": "修改成功"})
    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "msg": str(e)})

@csrf_exempt
@login_required
def register_competition(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        player_id = data.get("player_id")
        competition_id = data.get("competition_id")
        invite_code = (data.get("invite_code") or '').strip()
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
    if competition.type == 'PRIVATE':
        if not invite_code:
            return JsonResponse({"success": False, "msg": "私人赛需要提供邀请码"})
        if invite_code != competition.invite_code:
            return JsonResponse({"success": False, "msg": "邀请码错误"})
    models.Registration.objects.create(
        player=player,
        competition=competition,
        status=1,
        invite_code=invite_code,
        final_score='',
        final_rank=0,
        earned_points=0
    )

    return JsonResponse({"success": True, "msg": "报名成功"})


def generate_invite_code(length=6):
    code = string.ascii_uppercase + string.digits
    return ''.join(random.choice(code) for _ in range(length))


@csrf_exempt
def create_competition(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        title = data.get("title", "").strip()
        category = data.get("category", "").strip()
        location = data.get("location", "").strip()
        description = data.get("description", "").strip()
        competition_type = data.get("competition_type", "").strip()
        organizer_id = data.get("organizer_id")
        max_participants = data.get("max_participants", 100)
        reward_points = data.get("reward_points", 100)
        reward = data.get("reward", "").strip()
        start_time = data.get("start_time")
        end_time = data.get("end_time")
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"})
    if not title:
        return JsonResponse({"success": False, "msg": "标题不能为空"})
    organizer = models.User.objects.filter(
        id=organizer_id,
        role='ORGANIZER'
    ).first()
    if not organizer:
        return JsonResponse({"success": False, "msg": "主办方不存在"})
    status = 0 if competition_type == "PUBLIC" else 1
    invite_code = ''
    if competition_type == 'PRIVATE':
        invite_code = generate_invite_code()
    competition = models.Competition.objects.create(
        title=title,
        category=category,
        location=location,
        description=description,
        type=competition_type,
        organizer=organizer,
        status=status,
        max_participants=max_participants,
        current_participants=0,
        reward_points=reward_points,
        reward=reward,
        start_time=start_time,
        end_time=end_time,
        invite_code=invite_code
    )
    return JsonResponse({"success": True, "msg": "赛事创建成功", "competition_id": competition.id, "status": competition.status, "invite_code": invite_code})

@csrf_exempt
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
            "reward": c.reward,
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
@login_required
def review_competition(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"})

    admin = models.User.objects.filter(
        id=request.session.get("user_id"),
        role="ADMIN"
    ).first()

    if not admin:
        return JsonResponse({"success": False, "msg": "无管理员权限"}, status=403)

    try:
        data = json.loads(request.body)
        competition_id = data.get("competition_id")
        status = data.get("status")
        reason = (data.get("reason") or "").strip()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"})

    competition = models.Competition.objects.filter(id=competition_id).first()

    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"})

    if competition.status != 0:
        return JsonResponse({"success": False, "msg": "该赛事已审核"})

    if status == 1:
        competition.status = 1
        result = 1
    elif status == 4:
        competition.status = 4
        competition.reject_reason = reason
        result = 2
    else:
        return JsonResponse({"success": False, "msg": "非法审核状态"})

    competition.save()

    models.AuditRecord.objects.create(
        competition=competition,
        auditor=admin,
        result=result,
        remark=reason
    )

    return JsonResponse({"success": True, "msg": "审核完成"})

@csrf_exempt
def my_competitions(request):
    organizer_id = request.GET.get("organizer_id")
    status = request.GET.get("status", "")
    competition_type = request.GET.get("type", "")
    keyword = request.GET.get("keyword", "").strip()
    organizer = models.User.objects.filter(id=organizer_id,role='ORGANIZER').first()
    if not organizer:
        return JsonResponse({"success": False,"msg": "主办方不存在"})

    competitions = models.Competition.objects.filter(organizer=organizer)
    if status != "":
        competitions = competitions.filter(status=status)
    if competition_type:
        competitions = competitions.filter(type=competition_type)
    if keyword:
        competitions = competitions.filter(title__icontains=keyword)
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
            "invite_code": c.invite_code,
            "reject_reason": c.reject_reason
        })
    return JsonResponse({"success": True,"competitions": data})


@csrf_exempt
def delete_competition(request, competition_id):
    if request.method != "DELETE":
        return JsonResponse({"success": False,"msg": "仅支持 DELETE"})
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False,"msg": "赛事不存在"})
    competition.delete()
    return JsonResponse({"success": True,"msg": "删除成功"})

@csrf_exempt
def update_competition(request, competition_id):
    if request.method != "PUT":return JsonResponse({"success": False,"msg": "仅支持 PUT"})
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False,"msg": "赛事不存在"})
    try:
        data = json.loads(request.body)
        competition.title = data.get("title",competition.title)
        competition.category = data.get("category",competition.category)
        competition.location = data.get("location",competition.location)
        competition.description = data.get("description",competition.description)
        competition.max_participants = data.get("max_participants",competition.max_participants)
        competition.reward_points = data.get("reward_points",competition.reward_points)
        competition.reward = data.get("reward",competition.reward)
        competition.save()
    except Exception:
        return JsonResponse({"success": False,"msg": "请求格式错误"})

    return JsonResponse({"success": True,"msg": "修改成功"})

def competition_registrations(request, competition_id):
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False,"msg": "赛事不存在"})
    registrations = models.Registration.objects.filter(competition=competition)
    data = []
    for r in registrations:
        data.append({
            "registration_id": r.id,
            "player_id": r.player.id,
            "username": r.player.username,
            "nickname": r.player.nickname,
            "status": r.status,
            "review_status": r.review_status,
            "registration_time": r.registration_time
        })
    return JsonResponse({"success": True,"registrations": data})

@login_required
@csrf_exempt
def my_registrations(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"success": False, "msg": "未登录"})
    registrations = models.Registration.objects.filter(player=user_id).select_related("competition")
    result = []
    for reg in registrations:
        status_map = {
            0: "审核中",
            1: "报名成功",
            2: "已驳回"
        }
        result.append({
            "id": reg.id,
            "title": reg.competition.title,
            "time": reg.registration_time.strftime(
                "%Y-%m-%d %H:%M"
            ),
            "desc": reg.audit_remark or "",
            "status":
                "finished" if reg.review_status == 1
                else "processing",
            "statusText":
                status_map.get(reg.review_status, "未知状态")
        })
    return JsonResponse({"success": True,"data": result})

@login_required
@csrf_exempt
def cancel_registration(request):
    if request.method != "POST":
        return JsonResponse({"success": False,"msg": "仅支持POST"})
    try:
        data = json.loads(request.body)
        registration_id = data.get("registration_id")
    except:
        return JsonResponse({"success": False,"msg": "参数错误"})
    user_id = request.session.get("user_id")
    registration = models.Registration.objects.filter(id=registration_id,player_id=user_id).first()
    if not registration:
        return JsonResponse({"success": False,"msg": "报名记录不存在"})
    competition = registration.competition
    was_approved = registration.review_status == 1
    registration.delete()

    if was_approved and competition.current_participants > 0:
        competition.current_participants -= 1
        competition.save()
    return JsonResponse({"success": True,"msg": "取消报名成功"})

@csrf_exempt
@login_required
def approve_registration(request):
    if request.method != "POST":
        return JsonResponse({"success":False,"msg":"仅支持POST"})
    data = json.loads(request.body)
    registration_id = data.get("registration_id")
    reg = models.Registration.objects.filter(id=registration_id).first()
    if not reg:
        return JsonResponse({"success":False,"msg":"报名不存在"})
    if reg.review_status != 0:
        return JsonResponse({"success": False, "msg": "该报名已审核"})

    competition = reg.competition
    if competition.current_participants >= competition.max_participants:
        return JsonResponse({"success": False, "msg": "赛事人数已满"})
    reg.review_status = 1
    reg.audit_remark = "审核通过"
    reg.save()
    competition.current_participants += 1
    competition.save()
    return JsonResponse({"success":True,"msg":"审核通过"})

@csrf_exempt
@login_required
def reject_registration(request):
    if request.method != "POST":
        return JsonResponse({"success":False,"msg":"仅支持POST"})
    data = json.loads(request.body)
    registration_id = data.get("registration_id")
    remark = data.get("remark","")
    reg = models.Registration.objects.filter(id=registration_id).first()
    if not reg:
        return JsonResponse({"success":False,"msg":"报名不存在"})
    reg.review_status = 2
    reg.audit_remark = remark
    reg.save()
    return JsonResponse({"success":True,"msg":"已驳回"})

@csrf_exempt
@login_required
def admin_users(request):
    users = models.User.objects.all()
    data = []
    role_map = {"PLAYER": "选手","ORGANIZER": "主办方","ADMIN": "管理员"}
    for u in users:
        data.append({
            "user_id": u.id,
            "username": u.username,
            "role": role_map.get(u.role, u.role),
            "is_active": not u.is_deleted,
        })

    return JsonResponse({"success": True,"users": data})

@csrf_exempt
@login_required
def toggle_user_status(request, user_id):
    if request.method != "PUT":
        return JsonResponse({"success": False, "msg": "仅支持PUT"})

    data = json.loads(request.body)
    user = models.User.objects.filter(id=user_id).first()

    if not user:
        return JsonResponse({"success": False, "msg": "用户不存在"})

    is_active = data.get("is_active")
    user.is_deleted = not is_active
    user.save()

    msg = "用户已解封" if is_active else "用户已封禁"
    return JsonResponse({"success": True, "msg": msg})

@csrf_exempt
@login_required
def audit_records(request):
    records = models.AuditRecord.objects.all().order_by("-audit_time")
    data = []

    for r in records:
        data.append({
            "record_id": r.id,
            "competition_id": r.competition_id,
            "action": "通过" if r.result == 1 else "驳回",
            "created_at": r.audit_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return JsonResponse({"success": True, "records": data})