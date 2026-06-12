from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render, redirect
from pathlib import Path
from hashlib import md5
import hashlib
from app1 import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction, connection
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import json
import string
import random
import re
from functools import wraps
@csrf_exempt
def login(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        captcha = data.get("captcha", "").strip().upper()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if not username:
        return JsonResponse({"success": False, "msg": "用户名不能为空"})
    user = models.User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({"success": False, "msg": "用户不存在"})
    if user.is_deleted:
        return JsonResponse({"success": False, "msg": "该账号已被封禁"}, status=403)
    auto_login = is_auto_login_test_user(user) and not password and not captcha
    if not auto_login:
        if not password or not captcha:
            return JsonResponse({"success": False, "msg": "普通账号需要填写密码和验证码"})
        expected_captcha = request.session.get("login_captcha", "")
        if not expected_captcha or captcha != expected_captcha:
            return JsonResponse({"success": False, "msg": "验证码错误或已失效"})
        request.session.pop("login_captcha", None)
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        if user.password != password_md5:
            return JsonResponse({"success": False, "msg": "密码错误"})
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    return JsonResponse({
        "success": True,
        "msg": "测试账号免密码登录成功" if auto_login else "登录成功",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "is_super_admin": is_super_admin(user)
    })

@csrf_exempt
def logout(request):
    request.session.flush()
    return JsonResponse({"success": True, "msg": "退出登录"})

def login_captcha(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "msg": "仅支持 GET"}, status=405)
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    code = ''.join(random.SystemRandom().choice(alphabet) for _ in range(4))
    request.session["login_captcha"] = code
    return JsonResponse({"success": True, "captcha": code})

def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = models.User.objects.filter(
            id=request.session.get("user_id"),
            is_deleted=False
        ).first()
        if not user:
            request.session.flush()
            return JsonResponse({"success": False, "msg": "请先登录"}, status=401)
        request.current_user = user
        return func(request, *args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = models.User.objects.filter(
                id=request.session.get("user_id"),
                is_deleted=False
            ).first()
            if not user:
                request.session.flush()
                return JsonResponse({"success": False, "msg": "请先登录"}, status=401)
            if user.role != "ADMIN" and user.role not in roles:
                return JsonResponse({"success": False, "msg": "无操作权限"}, status=403)
            request.current_user = user
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def manageable_competitions(user):
    competitions = models.Competition.objects.all()
    if user.role == "ADMIN":
        return competitions
    return competitions.filter(organizer=user)

def manageable_registrations(user):
    registrations = models.Registration.objects.all()
    if user.role == "ADMIN":
        return registrations
    return registrations.filter(competition__organizer=user)

DEMO_LOCAL_TZ = timezone.get_fixed_timezone(8 * 60)

def parse_request_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = parse_datetime(text)
        if parsed is None:
            try:
                parsed = datetime.fromisoformat(text)
            except ValueError:
                return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed

def validate_competition_time(start_time, end_time):
    start_dt = parse_request_datetime(start_time)
    end_dt = parse_request_datetime(end_time)
    if not start_dt or not end_dt:
        return None, None, "请选择比赛开始和结束时间"
    today = timezone.localtime(timezone.now(), DEMO_LOCAL_TZ).date()
    start_day = timezone.localtime(start_dt, DEMO_LOCAL_TZ).date()
    end_day = timezone.localtime(end_dt, DEMO_LOCAL_TZ).date()
    if start_day < today or end_day < today:
        return None, None, "比赛日期不能早于今天"
    if end_dt <= start_dt:
        return None, None, "比赛结束时间必须晚于开始时间"
    return start_dt, end_dt, ""

def finish_expired_competitions():
    expired_ids = list(
        models.Competition.objects.filter(
            status__in=[1, 2],
            end_time__lte=timezone.now()
        ).values_list("id", flat=True)
    )
    if not expired_ids:
        return 0
    models.Competition.objects.filter(id__in=expired_ids).update(status=3)
    models.Registration.objects.filter(
        competition_id__in=expired_ids,
        review_status=0
    ).update(
        review_status=2,
        status="rejected",
        audit_remark="比赛已到结束时间，系统自动关闭报名"
    )
    return len(expired_ids)

def parse_bracket_state(competition):
    try:
        state = json.loads(competition.bracket_state or "{}")
    except (TypeError, json.JSONDecodeError):
        state = {}
    if not isinstance(state, dict):
        state = {}
    return {
        "drawSeed": state.get("drawSeed") or (competition.id * 100003),
        "winners": state.get("winners") if isinstance(state.get("winners"), dict) else {},
        "rankings": state.get("rankings") if isinstance(state.get("rankings"), list) else [],
        "seedIds": [str(item) for item in state.get("seedIds", [])] if isinstance(state.get("seedIds"), list) else [],
        "seedMode": "MANUAL" if state.get("seedMode") == "MANUAL" else "AUTO"
    }

def serialize_registration(registration):
    return {
        "registration_id": registration.id,
        "player_id": registration.player.id,
        "username": registration.player.username,
        "nickname": registration.player.nickname,
        "player_points": registration.player.points,
        "status": registration.status,
        "review_status": registration.review_status,
        "audit_remark": registration.audit_remark,
        "register_type": registration.register_type,
        "team_name": registration.team_name,
        "team_members": registration.team_members,
        "contact_name": registration.contact_name,
        "phone": registration.phone,
        "final_score": registration.final_score,
        "final_rank": registration.final_rank,
        "earned_points": registration.earned_points,
        "registration_time": registration.registration_time
    }

def can_view_competition_bracket(user, competition):
    if competition.type == "PUBLIC":
        return True
    if user.role == "ADMIN" or competition.organizer_id == user.id:
        return True
    return models.Registration.objects.filter(
        competition=competition,
        player=user,
        review_status__in=[0, 1]
    ).exists()

COMPETITION_FORMATS = {
    "SINGLE_ELIMINATION": "单淘汰",
}
DEFAULT_THUMBNAILS = {
    "篮球": "/default-thumbnails/basketball.png",
    "足球": "/default-thumbnails/football.png",
    "羽毛球": "/default-thumbnails/badminton.png",
    "网球": "/default-thumbnails/tennis.png",
    "电竞": "/default-thumbnails/esports.png",
    "棋牌桌游": "/default-thumbnails/boardgame.png",
}

def default_thumbnail_for_category(category):
    return DEFAULT_THUMBNAILS.get(category, "/default-thumbnails/badminton.png")

def generate_competition_no(competition_id):
    return f"NO.{int(competition_id):08d}"

def generate_user_code(user_id):
    return f"U{int(user_id):06d}"

def ensure_user_code(user):
    if user and not user.user_code:
        user.user_code = generate_user_code(user.id)
        user.save(update_fields=["user_code"])
    return user.user_code or generate_user_code(user.id)

def normalize_member_names(raw_text):
    names = [
        item.strip()
        for item in re.split(r"[\s,，、;；]+", raw_text or "")
        if item.strip()
    ]
    return list(dict.fromkeys(names))

def is_super_admin(user):
    return bool(user and user.role == "ADMIN" and user.username == "test_admin")

def is_auto_login_test_user(user):
    email = (user.email or "").lower()
    return bool(user and user.role != "ADMIN" and email.endswith("@lesai.test"))

def normalize_bracket_rankings(raw_rankings):
    if not isinstance(raw_rankings, list):
        return []
    rankings = []
    seen = set()
    for item in raw_rankings[:200]:
        if not isinstance(item, dict):
            continue
        try:
            registration_id = int(item.get("registration_id"))
            final_rank = int(item.get("final_rank"))
        except (TypeError, ValueError):
            continue
        if registration_id <= 0 or final_rank <= 0 or registration_id in seen:
            continue
        seen.add(registration_id)
        final_score = str(item.get("final_score") or "").strip()[:50]
        rankings.append({
            "registration_id": registration_id,
            "final_rank": final_rank,
            "final_score": final_score
        })
    return rankings

def apply_bracket_rankings(competition, rankings):
    approved = models.Registration.objects.filter(
        competition=competition,
        review_status=1
    )
    previous_awards = list(
        approved.filter(earned_points__gt=0).select_related("player")
    )
    for registration in previous_awards:
        player = registration.player
        player.points = max(0, (player.points or 0) - (registration.earned_points or 0))
        player.save(update_fields=["points"])

    approved.update(
        final_score="",
        final_rank=0,
        earned_points=0,
        status="ongoing"
    )
    registration_map = {
        item.id: item
        for item in approved.select_for_update().select_related("player")
    }
    try:
        public_champion_points = int(competition.reward_points or 0)
    except (TypeError, ValueError):
        public_champion_points = 0

    for ranking in rankings:
        registration = registration_map.get(ranking["registration_id"])
        if not registration:
            continue
        registration.final_rank = ranking["final_rank"]
        registration.final_score = ranking["final_score"]
        registration.earned_points = (
            public_champion_points
            if competition.type == "PUBLIC" and registration.final_rank == 1
            else 0
        )
        registration.status = "finished"
        registration.save(update_fields=["final_rank", "final_score", "earned_points", "status"])
        if registration.earned_points > 0:
            player = registration.player
            player.points = (player.points or 0) + registration.earned_points
            player.save(update_fields=["points"])

def delete_competitions_by_ids(competition_ids):
    competition_ids = [int(item) for item in competition_ids if item]
    if not competition_ids:
        return 0
    models.Registration.objects.filter(competition_id__in=competition_ids).delete()
    models.AuditRecord.objects.filter(competition_id__in=competition_ids).delete()
    placeholders = ", ".join(["%s"] * len(competition_ids))
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"DELETE FROM notice WHERE competition_id IN ({placeholders})", competition_ids)
        except Exception:
            pass
    deleted_count, _ = models.Competition.objects.filter(id__in=competition_ids).delete()
    return deleted_count

def delete_user_from_database(user, current_user):
    if not user or user.id == current_user.id:
        return False
    owned_competition_ids = list(
        models.Competition.objects.filter(organizer=user).values_list("id", flat=True)
    )
    delete_competitions_by_ids(owned_competition_ids)
    player_registrations = list(
        models.Registration.objects.select_related("competition")
        .filter(player=user)
        .exclude(competition_id__in=owned_competition_ids)
    )
    for registration in player_registrations:
        competition = registration.competition
        if registration.review_status == 1 and competition.current_participants > 0:
            competition.current_participants -= 1
            competition.save(update_fields=["current_participants"])
    ensure_friend_relation_table()
    models.FriendRelation.objects.filter(
        Q(requester=user) | Q(addressee=user)
    ).delete()
    models.FriendMessage.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).delete()
    models.Registration.objects.filter(player=user).delete()
    models.AuditRecord.objects.filter(auditor=user).delete()
    user.delete()
    return True

def unique_test_username(prefix):
    index = 1
    while True:
        username = f"{prefix}{index:02d}"
        if not models.User.objects.filter(username=username).exists():
            return username
        index += 1

def create_test_user(prefix="player_auto_", nickname_prefix="测试用户", role="PLAYER"):
    username = unique_test_username(prefix)
    user = models.User.objects.create(
        username=username,
        password=hashlib.md5("".encode()).hexdigest(),
        role=role,
        nickname=f"{nickname_prefix}{username[-2:]}",
        email=f"{username}@lesai.test",
        points=0,
        created_at=datetime.now(),
        is_deleted=False
    )
    ensure_user_code(user)
    return user

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
    if role not in {"PLAYER", "ORGANIZER", "ADMIN"}:
        return JsonResponse({"success": False, "msg": "用户角色错误"})
    if models.User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "msg": "用户名已存在"})
    password_md5 = hashlib.md5(password.encode()).hexdigest()
    user = models.User.objects.create(
        username=username,
        password=password_md5,
        nickname=nickname,
        email=email,
        points=0,
        created_at=datetime.now(),
        role=role
    )
    ensure_user_code(user)
    return JsonResponse({"success": True, "msg": "注册成功"})

@csrf_exempt
def competition_list(request):
    finish_expired_competitions()
    c_category = request.GET.get("category", "")
    keyword = request.GET.get("keyword", "").strip()
    competitions = models.Competition.objects.filter(status__in=[1, 2])
    if c_category:
        competitions = competitions.filter(category__icontains=c_category)
    if keyword:
        competitions = competitions.filter(
            Q(title__icontains=keyword) |
            Q(competition_no__icontains=keyword)
        )
    competitions = competitions.order_by("-created_at")
    data = []
    for c in competitions:
        data.append({
            "id": c.id,
            "competition_no": c.competition_no or generate_competition_no(c.id),
            "title": c.title,
            "category": c.category,
            "location": c.location,
            "description": c.description,
            "type": c.type,
            "status": c.status,
            "max_participants": c.max_participants,
            "current_participants": c.current_participants,
            "reward_points": c.reward_points,
            "thumbnail_url": c.thumbnail_url or "",
            "competition_format": c.competition_format,
            "competition_format_text": COMPETITION_FORMATS.get(c.competition_format, "单淘汰"),
            "group_count": c.group_count,
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
    finish_expired_competitions()
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"}, status=404)
    current_user = models.User.objects.filter(
        id=request.session.get("user_id"),
        is_deleted=False
    ).first()
    can_manage = bool(
        current_user and (
            current_user.role == "ADMIN" or competition.organizer_id == current_user.id
        )
    )
    data = {
        "id": competition.id,
        "competition_no": competition.competition_no or generate_competition_no(competition.id),
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
        "thumbnail_url": competition.thumbnail_url or "",
        "competition_format": competition.competition_format,
        "competition_format_text": COMPETITION_FORMATS.get(competition.competition_format, "单淘汰"),
        "group_count": competition.group_count,
        "start_time": competition.start_time,
        "end_time": competition.end_time,
        "created_at": competition.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "can_manage": can_manage,
    }
    if competition.type == "PRIVATE" and can_manage:
        data["invite_code"] = competition.invite_code
    return JsonResponse({"success": True, "data": data})

@csrf_exempt
@login_required
def user_detail(request):
    user = request.current_user
    data = {
        "id": user.id,
        "user_code": ensure_user_code(user),
        "username": user.username,
        "nickname": user.nickname,
        "email": user.email,
        "role": user.role,
        "points": user.points,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "is_deleted": user.is_deleted,
        "is_super_admin": is_super_admin(user),
    }
    return JsonResponse({"success": True, "data": data})

@csrf_exempt
@login_required
def upload_competition_thumbnail(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    file_obj = request.FILES.get("file")
    if not file_obj:
        return JsonResponse({"success": False, "msg": "请选择要上传的图片"}, status=400)
    if file_obj.size > 5 * 1024 * 1024:
        return JsonResponse({"success": False, "msg": "缩图不能超过5MB"}, status=400)

    suffix = Path(file_obj.name).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return JsonResponse({"success": False, "msg": "只支持 JPG、PNG、WEBP 或 GIF 图片"}, status=400)

    target_dir = Path(settings.MEDIA_ROOT) / "event_thumbnails"
    target_dir.mkdir(parents=True, exist_ok=True)
    random_part = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))
    filename = f"{request.current_user.id}_{int(timezone.now().timestamp())}_{random_part}{suffix}"
    target_path = target_dir / filename
    with target_path.open("wb") as target:
        for chunk in file_obj.chunks():
            target.write(chunk)

    relative_url = f"{settings.MEDIA_URL}event_thumbnails/{filename}"
    return JsonResponse({
        "success": True,
        "url": request.build_absolute_uri(relative_url),
        "msg": "缩图上传成功"
    })

@login_required
@csrf_exempt
def update_user(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "请求方式错误"})
    try:
        data = json.loads(request.body)
        user = request.current_user
        user.nickname = data.get("nickname", user.nickname)
        user.email = data.get("email", user.email)
        user.save()
        return JsonResponse({"success": True, "msg": "修改成功"})
    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "msg": str(e)})

@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
def register_competition(request):
    finish_expired_competitions()
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        competition_id = data.get("competition_id")
        invite_code = (data.get("invite_code") or '').strip()
        register_type = data.get("register_type", "single")
        team_name = data.get("team_name", "").strip()
        team_members = normalize_member_names(data.get("team_members", ""))
        contact_name = data.get("contact_name", "").strip()
        phone = data.get("phone", "").strip()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    player = request.current_user
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"})
    if competition.status != 1:
        return JsonResponse({"success": False, "msg": "当前赛事不可报名"})
    if player.role == "ORGANIZER" and not (
        competition.type == "PRIVATE" and competition.organizer_id == player.id
    ):
        return JsonResponse({"success": False, "msg": "主办方只能报名自己创建的私人赛事"}, status=403)
    if competition.current_participants >= competition.max_participants:
        return JsonResponse({"success": False, "msg": "赛事人数已满"})
    if models.Registration.objects.filter(player=player, competition=competition).exists():
        return JsonResponse({"success": False, "msg": "你已报名该赛事"})
    if register_type not in {"single", "team"}:
        return JsonResponse({"success": False, "msg": "报名类型错误"})
    if register_type == "team" and not team_name:
        return JsonResponse({"success": False, "msg": "战队报名需要填写战队名"})
    if register_type == "single":
        team_name = team_name or player.nickname or player.username
    if not team_members:
        return JsonResponse({"success": False, "msg": "请填写参赛选手账号"})
    if player.username not in team_members:
        return JsonResponse({"success": False, "msg": "选手账号列表必须包含当前登录账号"})
    if len(team_name) > 100 or len(contact_name) > 50 or len(phone) > 50:
        return JsonResponse({"success": False, "msg": "报名信息长度超出限制"})
    existing_users = set(models.User.objects.filter(
        username__in=team_members,
        is_deleted=False
    ).values_list("username", flat=True))
    missing_users = [name for name in team_members if name not in existing_users]
    if missing_users:
        return JsonResponse({
            "success": False,
            "msg": f"以下选手账号不存在或已被封禁：{', '.join(missing_users)}"
        })
    if competition.type == 'PRIVATE':
        if not invite_code:
            return JsonResponse({"success": False, "msg": "私人赛需要提供邀请码"})
        if invite_code != competition.invite_code:
            return JsonResponse({"success": False, "msg": "邀请码错误"})
    else:
        invite_code = ''
    auto_approve = competition.type == "PRIVATE" and competition.organizer_id == player.id
    models.Registration.objects.create(
        player=player,
        competition=competition,
        status='ongoing' if auto_approve else 'pending',
        review_status=1 if auto_approve else 0,
        invite_code=invite_code,
        register_type=register_type,
        team_name=team_name,
        team_members=', '.join(team_members),
        contact_name=contact_name or player.nickname or player.username,
        phone=phone or "系统消息通知",
        final_score='',
        final_rank=0,
        earned_points=0,
        audit_remark="创建者报名自动通过" if auto_approve else ""
    )
    if auto_approve:
        competition.current_participants += 1
        competition.save(update_fields=["current_participants"])

    return JsonResponse({
        "success": True,
        "msg": "报名成功，已自动通过" if auto_approve else "报名成功"
    })


def generate_invite_code(length=6):
    code = string.ascii_uppercase + string.digits
    return ''.join(random.choice(code) for _ in range(length))


@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
def create_competition(request):
    finish_expired_competitions()
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"}, status=405)
    try:
        data = json.loads(request.body)
        title = data.get("title", "").strip()
        category = data.get("category", "").strip()
        location = data.get("location", "").strip()
        description = data.get("description", "").strip()
        competition_type = data.get("competition_type", "").strip()
        max_participants = data.get("max_participants", 100)
        reward_points = data.get("reward_points", 100)
        reward = data.get("reward", "").strip()
        thumbnail_url = (data.get("thumbnail_url") or "").strip()
        competition_format = "SINGLE_ELIMINATION"
        group_count = data.get("group_count", 0)
        start_time = data.get("start_time")
        end_time = data.get("end_time")
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"})
    if not title or not category or not location:
        return JsonResponse({"success": False, "msg": "请填写完整赛事信息"})
    if competition_type not in {"PUBLIC", "PRIVATE"}:
        return JsonResponse({"success": False, "msg": "赛事类型错误"})
    if request.current_user.role == "PLAYER" and competition_type != "PRIVATE":
        return JsonResponse({"success": False, "msg": "参赛者只能创建私人赛事"}, status=403)
    try:
        max_participants = int(max_participants)
        reward_points = int(reward_points)
        group_count = 0
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "msg": "人数、积分和分组数必须是整数"})
    if competition_type == "PRIVATE":
        reward_points = 0
    if max_participants <= 0 or reward_points < 0:
        return JsonResponse({"success": False, "msg": "人数或积分设置不合法"})
    if len(thumbnail_url) > 500:
        return JsonResponse({"success": False, "msg": "缩图地址过长"})
    if not thumbnail_url:
        thumbnail_url = default_thumbnail_for_category(category)
    start_dt, end_dt, time_error = validate_competition_time(start_time, end_time)
    if time_error:
        return JsonResponse({"success": False, "msg": time_error})
    organizer = request.current_user
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
        competition_format=competition_format,
        group_count=group_count,
        start_time=start_dt,
        end_time=end_dt,
        invite_code=invite_code,
        thumbnail_url=thumbnail_url
    )
    competition.competition_no = generate_competition_no(competition.id)
    competition.save(update_fields=["competition_no"])
    return JsonResponse({
        "success": True,
        "msg": "赛事创建成功",
        "competition_id": competition.id,
        "competition_no": competition.competition_no,
        "status": competition.status,
        "invite_code": invite_code
    })

@csrf_exempt
@role_required("ADMIN")
def pending_competitions(request): #管理员查看待审核的赛事
    finish_expired_competitions()
    competitions = models.Competition.objects.filter(type='PUBLIC',status=0).order_by('-created_at')
    data = []
    for c in competitions:
        data.append({
            "id": c.id,
            "competition_no": c.competition_no or generate_competition_no(c.id),
            "title": c.title,
            "category": c.category,
            "location": c.location,
            "description": c.description,
            "reward": c.reward,
            "thumbnail_url": c.thumbnail_url or "",
            "max_participants": c.max_participants,
            "current_participants": c.current_participants,
            "reward_points": c.reward_points,
            "competition_format": c.competition_format,
            "competition_format_text": COMPETITION_FORMATS.get(c.competition_format, "单淘汰"),
            "group_count": c.group_count,
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
@role_required("ADMIN")
def review_competition(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"})

    admin = request.current_user

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
        if not reason:
            return JsonResponse({"success": False, "msg": "请填写驳回原因"})
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
@role_required("ORGANIZER", "PLAYER")
def my_competitions(request):
    finish_expired_competitions()
    status = request.GET.get("status", "")
    competition_type = request.GET.get("type", "")
    keyword = request.GET.get("keyword", "").strip()
    scope = request.GET.get("scope", "visible")
    if scope == "managed":
        competitions = manageable_competitions(request.current_user)
    elif request.current_user.role == "ADMIN":
        competitions = models.Competition.objects.all()
    else:
        joined_competition_ids = models.Registration.objects.filter(
            player=request.current_user,
            review_status__in=[0, 1]
        ).values_list("competition_id", flat=True)
        competitions = models.Competition.objects.filter(
            Q(organizer=request.current_user) | Q(id__in=joined_competition_ids)
        ).distinct()
    if status != "":
        competitions = competitions.filter(status=status)
    if competition_type:
        competitions = competitions.filter(type=competition_type)
    if keyword:
        competitions = competitions.filter(
            Q(title__icontains=keyword) |
            Q(competition_no__icontains=keyword)
        )
    competitions = competitions.order_by('-created_at')
    data = []
    for c in competitions:
        data.append({
            "id": c.id,
            "competition_no": c.competition_no or generate_competition_no(c.id),
            "title": c.title,
            "category": c.category,
            "location": c.location,
            "description": c.description,
            "type": c.type,
            "status": c.status,
            "max_participants": c.max_participants,
            "current_participants": c.current_participants,
            "reward_points": c.reward_points,
            "thumbnail_url": c.thumbnail_url or "",
            "competition_format": c.competition_format,
            "competition_format_text": COMPETITION_FORMATS.get(c.competition_format, "单淘汰"),
            "group_count": c.group_count,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "created_at": c.created_at,
            "invite_code": c.invite_code,
            "reject_reason": c.reject_reason,
            "can_manage": request.current_user.role == "ADMIN" or c.organizer_id == request.current_user.id
        })
    return JsonResponse({"success": True,"competitions": data})


@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
def delete_competition(request, competition_id):
    if request.method != "DELETE":
        return JsonResponse({"success": False,"msg": "仅支持 DELETE"})
    competition = manageable_competitions(request.current_user).filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False,"msg": "赛事不存在"})
    delete_competitions_by_ids([competition.id])
    return JsonResponse({"success": True,"msg": "删除成功"})

@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
def update_competition(request, competition_id):
    finish_expired_competitions()
    if request.method != "PUT":return JsonResponse({"success": False,"msg": "仅支持 PUT"})
    competition = manageable_competitions(request.current_user).filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False,"msg": "赛事不存在"})
    try:
        data = json.loads(request.body)
        competition.title = data.get("title",competition.title)
        competition.category = data.get("category",competition.category)
        competition.location = data.get("location",competition.location)
        competition.description = data.get("description",competition.description)
        max_participants = int(data.get("max_participants",competition.max_participants))
        reward_points = int(data.get("reward_points",competition.reward_points))
        competition_format = "SINGLE_ELIMINATION"
        group_count = 0
        if competition.type == "PRIVATE":
            reward_points = 0
        if max_participants < competition.current_participants or max_participants <= 0 or reward_points < 0:
            return JsonResponse({"success": False,"msg": "人数或积分设置不合法"})
        competition.max_participants = max_participants
        competition.reward_points = reward_points
        competition.competition_format = competition_format
        competition.group_count = group_count
        competition.reward = data.get("reward",competition.reward)
        competition.thumbnail_url = (data.get("thumbnail_url", competition.thumbnail_url) or "").strip()
        if competition.thumbnail_url and len(competition.thumbnail_url) > 500:
            return JsonResponse({"success": False,"msg": "缩图地址过长"})
        if not competition.thumbnail_url:
            competition.thumbnail_url = default_thumbnail_for_category(competition.category)
        if "start_time" in data or "end_time" in data:
            start_dt, end_dt, time_error = validate_competition_time(
                data.get("start_time", competition.start_time),
                data.get("end_time", competition.end_time)
            )
            if time_error:
                return JsonResponse({"success": False,"msg": time_error})
            competition.start_time = start_dt
            competition.end_time = end_dt
        competition.save()
    except Exception:
        return JsonResponse({"success": False,"msg": "请求格式错误"})

    return JsonResponse({"success": True,"msg": "修改成功"})

@login_required
def competition_registrations(request, competition_id):
    finish_expired_competitions()
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False,"msg": "赛事不存在"})
    if not can_view_competition_bracket(request.current_user, competition):
        return JsonResponse({"success": False, "msg": "暂无查看该赛事报名信息的权限"}, status=403)
    registrations = models.Registration.objects.filter(competition=competition)
    data = []
    for r in registrations:
        data.append(serialize_registration(r))
    return JsonResponse({
        "success": True,
        "registrations": data,
        "bracket_state": parse_bracket_state(competition)
    })

@login_required
@csrf_exempt
def competition_bracket(request, competition_id):
    finish_expired_competitions()
    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"}, status=404)

    if request.method == "GET":
        if not can_view_competition_bracket(request.current_user, competition):
            return JsonResponse({"success": False, "msg": "暂无查看该赛事赛程的权限"}, status=403)
        registrations = models.Registration.objects.filter(
            competition=competition,
            review_status=1
        ).select_related("player")
        return JsonResponse({
            "success": True,
            "registrations": [serialize_registration(reg) for reg in registrations],
            "bracket_state": parse_bracket_state(competition)
        })

    if request.method == "POST":
        editable_competition = manageable_competitions(request.current_user).filter(id=competition_id).first()
        if not editable_competition:
            return JsonResponse({"success": False, "msg": "暂无保存该赛事赛程的权限"}, status=403)
        try:
            data = json.loads(request.body)
            state = data.get("bracket_state", {})
        except (TypeError, json.JSONDecodeError):
            return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
        if not isinstance(state, dict):
            return JsonResponse({"success": False, "msg": "赛程数据格式错误"}, status=400)
        winners = state.get("winners", {})
        if not isinstance(winners, dict):
            winners = {}
        rankings = normalize_bracket_rankings(state.get("rankings", []))
        raw_seed_ids = state.get("seedIds", [])
        if not isinstance(raw_seed_ids, list):
            raw_seed_ids = []
        approved_ids = set(
            str(item)
            for item in models.Registration.objects.filter(
                competition=editable_competition,
                review_status=1
            ).values_list("id", flat=True)
        )
        seed_ids = []
        for item in raw_seed_ids[:16]:
            value = str(item).strip()
            if value in approved_ids and value not in seed_ids:
                seed_ids.append(value)
        safe_state = {
            "drawSeed": state.get("drawSeed") or (competition.id * 100003),
            "winners": winners,
            "rankings": rankings,
            "seedIds": seed_ids,
            "seedMode": "MANUAL" if state.get("seedMode") == "MANUAL" else "AUTO"
        }
        with transaction.atomic():
            editable_competition.bracket_state = json.dumps(safe_state, ensure_ascii=False)
            editable_competition.save(update_fields=["bracket_state"])
            apply_bracket_rankings(editable_competition, rankings)
        return JsonResponse({
            "success": True,
            "msg": "赛程已保存",
            "bracket_state": safe_state
        })

    return JsonResponse({"success": False, "msg": "请求方法不支持"}, status=405)

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
        status_text = "已完赛" if reg.status == "finished" else status_map.get(
            reg.review_status,
            "未知状态"
        )
        display_status = (
            "finished" if reg.status == "finished"
            else "rejected" if reg.review_status == 2
            else "ongoing" if reg.review_status == 1
            else "processing"
        )
        description = reg.audit_remark or ""
        if reg.status == "finished":
            score_text = f"成绩：{reg.final_score or '-'}，排名：{reg.final_rank or '-'}"
            if reg.competition.type != "PRIVATE":
                score_text += f"，获得积分：{reg.earned_points or 0}"
            description = score_text
        result.append({
            "id": reg.id,
            "competitionId": reg.competition.id,
            "title": reg.competition.title,
            "competitionType": reg.competition.type,
            "competitionTypeText": "私人赛" if reg.competition.type == "PRIVATE" else "公开赛",
            "participantCount": reg.competition.current_participants,
            "maxParticipants": reg.competition.max_participants,
            "finalScore": reg.final_score or "",
            "finalRank": reg.final_rank or 0,
            "earnedPoints": reg.earned_points or 0,
            "isFinished": reg.status == "finished",
            "time": reg.registration_time.strftime(
                "%Y-%m-%d %H:%M"
            ),
            "desc": description,
            "status": display_status,
            "statusText": status_text,
            "canCancel": reg.competition.status == 1 and reg.status != "finished",
            "showInProfile": reg.show_in_profile
        })
    return JsonResponse({"success": True,"data": result})

@login_required
@csrf_exempt
def update_registration_visibility(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        registration_id = data.get("registration_id")
        show_in_profile = bool(data.get("show_in_profile"))
    except Exception:
        return JsonResponse({"success": False, "msg": "参数错误"}, status=400)
    registration = models.Registration.objects.filter(
        id=registration_id,
        player=request.current_user
    ).first()
    if not registration:
        return JsonResponse({"success": False, "msg": "报名记录不存在"}, status=404)
    registration.show_in_profile = show_in_profile
    registration.save(update_fields=["show_in_profile"])
    return JsonResponse({"success": True, "msg": "参赛痕迹展示设置已保存"})

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
    if competition.status != 1 or registration.status == "finished":
        return JsonResponse({"success": False, "msg": "当前报名不可取消"})
    was_approved = registration.review_status == 1
    registration.delete()

    if was_approved and competition.current_participants > 0:
        competition.current_participants -= 1
        competition.save()
    return JsonResponse({"success": True,"msg": "取消报名成功"})

@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
def approve_registration(request):
    if request.method != "POST":
        return JsonResponse({"success":False,"msg":"仅支持POST"})
    try:
        data = json.loads(request.body)
        registration_id = data.get("registration_id")
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    reg = manageable_registrations(request.current_user).filter(id=registration_id).first()
    if not reg:
        return JsonResponse({"success":False,"msg":"报名不存在"})
    if reg.review_status != 0:
        return JsonResponse({"success": False, "msg": "该报名已审核"})

    competition = reg.competition
    if competition.current_participants >= competition.max_participants:
        return JsonResponse({"success": False, "msg": "赛事人数已满"})
    reg.review_status = 1
    reg.status = 'ongoing'
    reg.audit_remark = "审核通过"
    reg.save()
    competition.current_participants += 1
    competition.save()
    return JsonResponse({"success":True,"msg":"审核通过"})

@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
def reject_registration(request):
    if request.method != "POST":
        return JsonResponse({"success":False,"msg":"仅支持POST"})
    try:
        data = json.loads(request.body)
        registration_id = data.get("registration_id")
        remark = data.get("remark","")
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    reg = manageable_registrations(request.current_user).filter(id=registration_id).first()
    if not reg:
        return JsonResponse({"success":False,"msg":"报名不存在"})
    if reg.review_status != 0:
        return JsonResponse({"success": False, "msg": "该报名已审核"})
    reg.review_status = 2
    reg.status = 'rejected'
    reg.audit_remark = remark
    reg.save()
    return JsonResponse({"success":True,"msg":"已驳回"})

@csrf_exempt
@role_required("ADMIN")
def admin_force_registration(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        competition_id = data.get("competition_id")
        username = data.get("username", "").strip()
        register_type = data.get("register_type", "single")
        team_name = data.get("team_name", "").strip()
        team_members = normalize_member_names(data.get("team_members", username))
        contact_name = data.get("contact_name", "").strip()
        phone = data.get("phone", "").strip()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)

    competition = models.Competition.objects.filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"}, status=404)
    player = models.User.objects.filter(username=username, is_deleted=False).first()
    if not player:
        return JsonResponse({"success": False, "msg": "要加入的用户不存在或已被封禁"})
    if register_type not in {"single", "team"}:
        return JsonResponse({"success": False, "msg": "报名类型错误"})
    if register_type == "single":
        team_name = team_name or player.nickname or player.username
    if register_type == "team" and not team_name:
        return JsonResponse({"success": False, "msg": "战队报名需要填写战队名"})
    if not team_members:
        team_members = [player.username]
    if player.username not in team_members:
        team_members.insert(0, player.username)

    existing_users = set(models.User.objects.filter(
        username__in=team_members,
        is_deleted=False
    ).values_list("username", flat=True))
    missing_users = [name for name in team_members if name not in existing_users]
    if missing_users:
        return JsonResponse({
            "success": False,
            "msg": f"以下选手账号不存在或已被封禁：{', '.join(missing_users)}"
        })
    if models.Registration.objects.filter(player=player, competition=competition).exists():
        return JsonResponse({"success": False, "msg": "该用户已经在这个赛事中"})
    if competition.current_participants >= competition.max_participants:
        return JsonResponse({"success": False, "msg": "赛事人数已满"})

    models.Registration.objects.create(
        player=player,
        competition=competition,
        status="ongoing",
        review_status=1,
        register_type=register_type,
        team_name=team_name,
        team_members=", ".join(team_members),
        contact_name=contact_name or player.nickname or player.username,
        phone=phone,
        invite_code=competition.invite_code if competition.type == "PRIVATE" else "",
        final_score="",
        final_rank=0,
        earned_points=0,
        audit_remark="管理员测试加入"
    )
    competition.current_participants += 1
    competition.save(update_fields=["current_participants"])
    return JsonResponse({"success": True, "msg": "已将用户加入赛事"})

@csrf_exempt
@role_required("ADMIN")
def admin_delete_registration(request, registration_id):
    if request.method != "DELETE":
        return JsonResponse({"success": False, "msg": "仅支持DELETE"}, status=405)
    registration = models.Registration.objects.select_related("competition").filter(
        id=registration_id
    ).first()
    if not registration:
        return JsonResponse({"success": False, "msg": "报名记录不存在"}, status=404)
    competition = registration.competition
    was_counted = registration.review_status == 1 and competition.current_participants > 0
    registration.delete()
    if was_counted:
        competition.current_participants -= 1
        competition.save(update_fields=["current_participants"])
    return JsonResponse({"success": True, "msg": "报名记录已删除"})

@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
@transaction.atomic
def update_registration_status(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        registration_id = data.get("registration_id")
        target_status = str(data.get("status", "")).strip()
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)

    status_map = {
        "pending": (0, "pending", "已改为待审核"),
        "approved": (1, "ongoing", "已改为报名通过"),
        "rejected": (2, "rejected", "已改为驳回"),
        "ongoing": (1, "ongoing", "已改为进行中"),
        "finished": (1, "finished", "已改为已完赛"),
    }
    if target_status not in status_map:
        return JsonResponse({"success": False, "msg": "选手状态不正确"}, status=400)

    registration = manageable_registrations(request.current_user).select_for_update().filter(
        id=registration_id
    ).select_related("competition").first()
    if not registration:
        return JsonResponse({"success": False, "msg": "报名记录不存在"}, status=404)

    competition = registration.competition
    was_counted = registration.review_status == 1
    next_review_status, next_status, remark = status_map[target_status]
    will_count = next_review_status == 1

    if not was_counted and will_count and competition.current_participants >= competition.max_participants:
        return JsonResponse({"success": False, "msg": "赛事人数已满"})

    registration.review_status = next_review_status
    registration.status = next_status
    registration.audit_remark = remark
    registration.save(update_fields=["review_status", "status", "audit_remark"])

    if was_counted and not will_count and competition.current_participants > 0:
        competition.current_participants -= 1
        competition.save(update_fields=["current_participants"])
    elif not was_counted and will_count:
        competition.current_participants += 1
        competition.save(update_fields=["current_participants"])

    return JsonResponse({"success": True, "msg": remark})

@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
def update_competition_status(request, competition_id):
    finish_expired_competitions()
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    competition = manageable_competitions(request.current_user).filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"})
    try:
        data = json.loads(request.body)
        new_status = int(data.get("status"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)

    if (competition.status, new_status) not in {(1, 2), (1, 3), (2, 3)}:
        return JsonResponse({"success": False, "msg": "赛事状态不可这样修改"})

    competition.status = new_status
    competition.save()
    if new_status == 2:
        models.Registration.objects.filter(
            competition=competition,
            review_status=1
        ).exclude(status='finished').update(status='ongoing')
        models.Registration.objects.filter(
            competition=competition,
            review_status=0
        ).update(
            review_status=2,
            status="rejected",
            audit_remark="赛事已开始，未通过报名自动驳回"
        )

    return JsonResponse({"success": True, "msg": "赛事状态已更新"})

@csrf_exempt
@role_required("ORGANIZER", "PLAYER")
@transaction.atomic
def record_result(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        registration_id = data.get("registration_id")
        final_score = str(data.get("final_score", "")).strip()
        final_rank = int(data.get("final_rank", 0))
        earned_points = int(data.get("earned_points", 0))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)

    if final_rank <= 0 or earned_points < 0:
        return JsonResponse({"success": False, "msg": "排名或积分设置不合法"})

    registration = manageable_registrations(request.current_user).select_for_update().filter(
        id=registration_id
    ).select_related("player", "competition").first()
    if not registration:
        return JsonResponse({"success": False, "msg": "报名记录不存在"})
    if registration.review_status != 1:
        return JsonResponse({"success": False, "msg": "仅能为审核通过的选手录入成绩"})
    if registration.competition.status not in {2, 3}:
        return JsonResponse({"success": False, "msg": "赛事尚未开始"})
    if registration.status == "finished":
        return JsonResponse({"success": False, "msg": "该选手成绩已录入"})
    if registration.competition.type == "PRIVATE":
        earned_points = 0

    registration.final_score = final_score
    registration.final_rank = final_rank
    registration.earned_points = earned_points
    registration.status = "finished"
    registration.save()

    if earned_points > 0:
        player = registration.player
        player.points = (player.points or 0) + earned_points
        player.save()
        models.Point_history.objects.create(
            username=player.username,
            change_amount=earned_points,
            reason=f"参加[{registration.competition.title}]获得第{final_rank}名"[:100]
        )
    return JsonResponse({"success": True, "msg": "成绩与积分已保存"})

@csrf_exempt
@role_required("ADMIN")
def admin_users(request):
    users = models.User.objects.all()
    data = []
    role_map = {"PLAYER": "选手","ORGANIZER": "主办方","ADMIN": "管理员"}
    for u in users:
        data.append({
            "user_id": u.id,
            "user_code": ensure_user_code(u),
            "username": u.username,
            "nickname": u.nickname,
            "email": u.email,
            "role_code": u.role,
            "role": role_map.get(u.role, u.role),
            "is_active": not u.is_deleted,
            "is_super_admin": is_super_admin(u),
        })

    return JsonResponse({"success": True,"users": data})

@csrf_exempt
@role_required("ADMIN")
def admin_create_user(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "PLAYER").strip().upper()
        nickname = data.get("nickname", username).strip()
        email = data.get("email", "").strip()
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if not username or not password:
        return JsonResponse({"success": False, "msg": "用户名和密码不能为空"})
    if role not in {"PLAYER", "ORGANIZER", "ADMIN"}:
        return JsonResponse({"success": False, "msg": "用户角色错误"})
    if role == "ADMIN" and not is_super_admin(request.current_user):
        return JsonResponse({"success": False, "msg": "只有 test_admin 可以创建管理员账号"}, status=403)
    if len(username) > 50 or len(nickname) > 50:
        return JsonResponse({"success": False, "msg": "用户名或昵称过长"})
    if models.User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "msg": "用户名已存在"})
    user = models.User.objects.create(
        username=username,
        password=hashlib.md5(password.encode()).hexdigest(),
        role=role,
        nickname=nickname,
        email=email,
        points=0,
        created_at=datetime.now(),
        is_deleted=False
    )
    ensure_user_code(user)
    return JsonResponse({"success": True, "msg": "用户创建成功", "user_id": user.id, "user_code": user.user_code})

@csrf_exempt
@role_required("ADMIN")
def admin_bulk_create_users(request):
    if not is_super_admin(request.current_user):
        return JsonResponse({"success": False, "msg": "只有 test_admin 可以批量新增用户"}, status=403)
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        prefix = data.get("prefix", "player_auto_").strip()
        count = int(data.get("count", 5))
        role = data.get("role", "PLAYER").strip().upper()
        password = data.get("password", "123456").strip() or "123456"
        nickname_prefix = data.get("nickname_prefix", "测试用户").strip() or "测试用户"
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if role not in {"PLAYER", "ORGANIZER", "ADMIN"}:
        return JsonResponse({"success": False, "msg": "用户角色错误"})
    if not prefix or len(prefix) > 40:
        return JsonResponse({"success": False, "msg": "账号前缀不能为空且不能过长"})
    if count <= 0 or count > 100:
        return JsonResponse({"success": False, "msg": "一次最多批量新增100个用户"})

    created = []
    password_hash = hashlib.md5(password.encode()).hexdigest()
    index = 1
    attempts = 0
    while len(created) < count and attempts < count * 20:
        username = f"{prefix}{index:02d}"
        attempts += 1
        index += 1
        if models.User.objects.filter(username=username).exists():
            continue
        user = models.User.objects.create(
            username=username,
            password=password_hash,
            role=role,
            nickname=f"{nickname_prefix}{len(created) + 1}",
            email=f"{username}@lesai.test",
            points=0,
            created_at=datetime.now(),
            is_deleted=False
        )
        ensure_user_code(user)
        created.append({
            "user_id": user.id,
            "user_code": user.user_code,
            "username": user.username,
            "nickname": user.nickname,
            "role": user.role
        })

    return JsonResponse({
        "success": True,
        "msg": f"已新增 {len(created)} 个用户",
        "users": created
    })

@csrf_exempt
@role_required("ADMIN")
@transaction.atomic
def admin_bulk_force_registration(request):
    if not is_super_admin(request.current_user):
        return JsonResponse({"success": False, "msg": "只有 test_admin 可以批量加入比赛"}, status=403)
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        competition_id = data.get("competition_id")
        user_ids = data.get("user_ids", [])
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if not isinstance(user_ids, list) or not user_ids:
        return JsonResponse({"success": False, "msg": "请选择要加入比赛的用户"})

    competition = models.Competition.objects.select_for_update().filter(id=competition_id).first()
    if not competition:
        return JsonResponse({"success": False, "msg": "赛事不存在"}, status=404)

    users = list(models.User.objects.filter(
        id__in=user_ids,
        is_deleted=False
    ).exclude(role="ADMIN"))
    if not users:
        return JsonResponse({"success": False, "msg": "没有可加入比赛的普通用户或主办方"})

    created = []
    skipped = []
    remaining = max(0, competition.max_participants - competition.current_participants)
    existing_player_ids = set(models.Registration.objects.filter(
        competition=competition,
        player_id__in=[user.id for user in users]
    ).values_list("player_id", flat=True))

    for user in users:
        if user.id in existing_player_ids:
            skipped.append({"username": user.username, "reason": "已在该赛事中"})
            continue
        if remaining <= 0:
            skipped.append({"username": user.username, "reason": "赛事人数已满"})
            continue
        registration = models.Registration.objects.create(
            player=user,
            competition=competition,
            status="ongoing",
            review_status=1,
            register_type="single",
            team_name=user.nickname or user.username,
            team_members=user.username,
            contact_name=user.nickname or user.username,
            phone="test_admin批量加入",
            invite_code=competition.invite_code if competition.type == "PRIVATE" else "",
            final_score="",
            final_rank=0,
            earned_points=0,
            audit_remark="test_admin批量加入"
        )
        created.append({
            "registration_id": registration.id,
            "username": user.username,
            "team_name": registration.team_name
        })
        remaining -= 1

    if created:
        competition.current_participants += len(created)
        competition.save(update_fields=["current_participants"])

    return JsonResponse({
        "success": True,
        "msg": f"已加入 {len(created)} 个用户，跳过 {len(skipped)} 个",
        "created": created,
        "skipped": skipped
    })

@csrf_exempt
@role_required("ADMIN")
@transaction.atomic
def admin_bulk_create_competitions(request):
    if not is_super_admin(request.current_user):
        return JsonResponse({"success": False, "msg": "只有 test_admin 可以批量新增赛事"}, status=403)
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        count = int(data.get("count", 3))
        max_participants = int(data.get("max_participants", 8))
        competition_type = str(data.get("type", "PUBLIC")).upper()
        auto_fill = bool(data.get("auto_fill", False))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if count <= 0 or count > 30:
        return JsonResponse({"success": False, "msg": "一次最多批量新增30个赛事"})
    if max_participants <= 1 or max_participants > 64:
        return JsonResponse({"success": False, "msg": "每个赛事人数需在2到64之间"})
    if competition_type not in {"PUBLIC", "PRIVATE", "MIXED"}:
        return JsonResponse({"success": False, "msg": "赛事类型错误"})

    categories = ["羽毛球", "篮球", "足球", "网球", "电竞", "棋牌桌游"]
    locations = ["市体育馆", "大学球场", "校内体育馆", "线上", "活动中心"]
    created = []
    for index in range(count):
        c_type = random.choice(["PUBLIC", "PRIVATE"]) if competition_type == "MIXED" else competition_type
        category = random.choice(categories)
        start_time = datetime.now() + timedelta(days=index + 1, hours=random.randint(8, 18))
        end_time = start_time + timedelta(hours=3)
        competition = models.Competition.objects.create(
            title=f"测试{category}单淘汰赛{index + 1:02d}",
            category=category,
            location=random.choice(locations),
            description="test_admin 批量生成的演示赛事",
            type=c_type,
            organizer=request.current_user,
            status=1,
            max_participants=max_participants,
            current_participants=0,
            reward_points=0 if c_type == "PRIVATE" else random.choice([50, 100, 150, 200]),
            reward="测试赛事奖励" if c_type == "PUBLIC" else "私人赛无积分",
            competition_format="SINGLE_ELIMINATION",
            group_count=0,
            start_time=start_time,
            end_time=end_time,
            invite_code=generate_invite_code() if c_type == "PRIVATE" else None,
            thumbnail_url=default_thumbnail_for_category(category)
        )
        competition.competition_no = generate_competition_no(competition.id)
        competition.save(update_fields=["competition_no"])
        if auto_fill:
            for _ in range(max_participants):
                player = create_test_user(prefix="auto_player_", nickname_prefix="自动选手", role="PLAYER")
                models.Registration.objects.create(
                    player=player,
                    competition=competition,
                    status="ongoing",
                    review_status=1,
                    register_type="single",
                    team_name=player.nickname or player.username,
                    team_members=player.username,
                    contact_name=player.nickname or player.username,
                    phone="系统消息通知",
                    invite_code=competition.invite_code if competition.type == "PRIVATE" else "",
                    final_score="",
                    final_rank=0,
                    earned_points=0,
                    audit_remark="test_admin随机填满"
                )
            competition.current_participants = max_participants
            competition.save(update_fields=["current_participants"])
        created.append({
            "id": competition.id,
            "competition_no": competition.competition_no,
            "title": competition.title,
            "filled": auto_fill
        })
    return JsonResponse({"success": True, "msg": f"已新增 {len(created)} 个赛事", "competitions": created})

@csrf_exempt
@role_required("ADMIN")
@transaction.atomic
def admin_bulk_delete_competitions(request):
    if not is_super_admin(request.current_user):
        return JsonResponse({"success": False, "msg": "只有 test_admin 可以批量删除赛事"}, status=403)
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        competition_ids = data.get("competition_ids", [])
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if not isinstance(competition_ids, list) or not competition_ids:
        return JsonResponse({"success": False, "msg": "请选择要删除的赛事"})
    deleted_count = delete_competitions_by_ids(competition_ids)
    return JsonResponse({"success": True, "msg": f"已删除 {deleted_count} 个赛事"})

@csrf_exempt
@role_required("ADMIN")
@transaction.atomic
def admin_bulk_delete_users(request):
    if not is_super_admin(request.current_user):
        return JsonResponse({"success": False, "msg": "只有 test_admin 可以批量删除用户"}, status=403)
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    try:
        data = json.loads(request.body)
        user_ids = data.get("user_ids", [])
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    if not isinstance(user_ids, list) or not user_ids:
        return JsonResponse({"success": False, "msg": "请选择要删除的用户"})
    deleted = 0
    for user in models.User.objects.filter(id__in=user_ids):
        if delete_user_from_database(user, request.current_user):
            deleted += 1
    return JsonResponse({"success": True, "msg": f"已删除 {deleted} 个用户"})

@csrf_exempt
@role_required("ADMIN")
def toggle_user_status(request, user_id):
    if request.method != "PUT":
        return JsonResponse({"success": False, "msg": "仅支持PUT"})

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    user = models.User.objects.filter(id=user_id).first()

    if not user:
        return JsonResponse({"success": False, "msg": "用户不存在"})
    if user.id == request.current_user.id:
        return JsonResponse({"success": False, "msg": "不能封禁当前管理员账号"})

    is_active = data.get("is_active")
    if not isinstance(is_active, bool):
        return JsonResponse({"success": False, "msg": "用户状态参数错误"})
    user.is_deleted = not is_active
    user.save()

    msg = "用户已解封" if is_active else "用户已封禁"
    return JsonResponse({"success": True, "msg": msg})

@csrf_exempt
@role_required("ADMIN")
@transaction.atomic
def admin_delete_user(request, user_id):
    if not is_super_admin(request.current_user):
        return JsonResponse({"success": False, "msg": "只有 test_admin 可以彻底删除账号"}, status=403)
    if request.method != "DELETE":
        return JsonResponse({"success": False, "msg": "仅支持DELETE"}, status=405)
    user = models.User.objects.select_for_update().filter(id=user_id).first()
    if not user:
        return JsonResponse({"success": False, "msg": "用户不存在"}, status=404)
    if not delete_user_from_database(user, request.current_user):
        return JsonResponse({"success": False, "msg": "不能删除当前登录账号"})
    return JsonResponse({"success": True, "msg": "账号已从数据库删除"})

@csrf_exempt
@role_required("ADMIN")
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

def ensure_friend_relation_table():
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friend_relation (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                requester_id BIGINT NOT NULL,
                addressee_id BIGINT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY uniq_friend_pair (requester_id, addressee_id),
                KEY idx_friend_requester (requester_id),
                KEY idx_friend_addressee (addressee_id),
                KEY idx_friend_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friend_message (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                sender_id BIGINT NOT NULL,
                receiver_id BIGINT NOT NULL,
                content VARCHAR(500) NOT NULL,
                is_read TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                KEY idx_friend_message_pair (sender_id, receiver_id, created_at),
                KEY idx_friend_message_unread (receiver_id, is_read)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

def relation_between_users(user_id, target_id):
    return models.FriendRelation.objects.filter(
        Q(requester_id=user_id, addressee_id=target_id) |
        Q(requester_id=target_id, addressee_id=user_id)
    ).first()

def accepted_relation_between_users(user_id, target_id):
    return models.FriendRelation.objects.filter(
        status="accepted"
    ).filter(
        Q(requester_id=user_id, addressee_id=target_id) |
        Q(requester_id=target_id, addressee_id=user_id)
    ).first()

def serialize_friend_user(user, relation=None, current_user=None):
    payload = {
        "user_id": user.id,
        "user_code": ensure_user_code(user),
        "username": user.username,
        "nickname": user.nickname,
        "role": user.role,
        "points": user.points,
        "allow_friend_requests": bool(user.allow_friend_requests),
        "can_request_friend": bool(user.allow_friend_requests),
    }
    if relation:
        payload["relation_id"] = relation.id
        payload["relation_status"] = relation.status
        payload["can_request_friend"] = relation.status not in {"accepted", "pending"}
        if current_user and relation.status == "pending":
            payload["relation_direction"] = "incoming" if relation.addressee_id == current_user.id else "outgoing"
        elif relation.status == "accepted":
            payload["relation_direction"] = "friend"
    return payload

@login_required
def friends(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "msg": "仅支持GET"}, status=405)
    ensure_friend_relation_table()
    user = request.current_user
    accepted = models.FriendRelation.objects.filter(
        status="accepted"
    ).filter(
        Q(requester=user) | Q(addressee=user)
    ).select_related("requester", "addressee").order_by("-updated_at")
    pending_incoming = models.FriendRelation.objects.filter(
        addressee=user,
        status="pending"
    ).select_related("requester").order_by("-created_at")
    pending_outgoing = models.FriendRelation.objects.filter(
        requester=user,
        status="pending"
    ).select_related("addressee").order_by("-created_at")

    friend_list = []
    for relation in accepted:
        friend = relation.addressee if relation.requester_id == user.id else relation.requester
        friend_payload = serialize_friend_user(friend, relation, user)
        unread_count = models.FriendMessage.objects.filter(
            sender=friend,
            receiver=user,
            is_read=False
        ).count()
        last_message = models.FriendMessage.objects.filter(
            Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
        ).order_by("-created_at").first()
        friend_payload["unread_count"] = unread_count
        friend_payload["last_message"] = last_message.content if last_message else ""
        friend_payload["last_message_time"] = last_message.created_at.strftime("%Y-%m-%d %H:%M") if last_message else ""
        friend_list.append(friend_payload)

    return JsonResponse({
        "success": True,
        "allow_friend_requests": bool(user.allow_friend_requests),
        "friends": friend_list,
        "incoming": [
            serialize_friend_user(relation.requester, relation, user)
            for relation in pending_incoming
        ],
        "outgoing": [
            serialize_friend_user(relation.addressee, relation, user)
            for relation in pending_outgoing
        ]
    })

@login_required
def friend_search(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "msg": "仅支持GET"}, status=405)
    ensure_friend_relation_table()
    user = request.current_user
    keyword = request.GET.get("keyword", "").strip()
    users = models.User.objects.filter(is_deleted=False).exclude(id=user.id)
    if keyword:
        users = users.filter(
            Q(username__icontains=keyword) |
            Q(nickname__icontains=keyword) |
            Q(user_code__icontains=keyword)
        )
    users = list(users.order_by("-points", "username")[:30])
    relation_map = {}
    for relation in models.FriendRelation.objects.filter(
        Q(requester=user, addressee_id__in=[item.id for item in users]) |
        Q(addressee=user, requester_id__in=[item.id for item in users])
    ):
        other_id = relation.addressee_id if relation.requester_id == user.id else relation.requester_id
        relation_map[other_id] = relation
    return JsonResponse({
        "success": True,
        "users": [
            serialize_friend_user(item, relation_map.get(item.id), user)
            for item in users
        ]
    })

@csrf_exempt
@login_required
def send_friend_request(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    ensure_friend_relation_table()
    try:
        data = json.loads(request.body)
        target_id = int(data.get("user_id"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    user = request.current_user
    if target_id == user.id:
        return JsonResponse({"success": False, "msg": "不能添加自己为好友"})
    target = models.User.objects.filter(id=target_id, is_deleted=False).first()
    if not target:
        return JsonResponse({"success": False, "msg": "用户不存在或已被封禁"})
    relation = relation_between_users(user.id, target.id)
    if relation:
        if relation.status == "accepted":
            return JsonResponse({"success": False, "msg": "已经是好友"})
        if relation.status == "pending" and relation.addressee_id == user.id:
            relation.status = "accepted"
            relation.save(update_fields=["status", "updated_at"])
            return JsonResponse({"success": True, "msg": "已通过对方的好友申请"})
        if relation.status == "pending":
            return JsonResponse({"success": False, "msg": "好友申请已发送，请等待对方处理"})
        if not target.allow_friend_requests:
            return JsonResponse({"success": False, "msg": "对方已关闭好友申请"})
        relation.requester = user
        relation.addressee = target
        relation.status = "pending"
        relation.save(update_fields=["requester", "addressee", "status", "updated_at"])
    else:
        if not target.allow_friend_requests:
            return JsonResponse({"success": False, "msg": "对方已关闭好友申请"})
        relation = models.FriendRelation.objects.create(
            requester=user,
            addressee=target,
            status="pending"
        )
    return JsonResponse({"success": True, "msg": "好友申请已发送", "relation_id": relation.id})

@csrf_exempt
@login_required
def respond_friend_request(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持POST"}, status=405)
    ensure_friend_relation_table()
    try:
        data = json.loads(request.body)
        relation_id = int(data.get("relation_id"))
        action = str(data.get("action", "")).strip()
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    relation = models.FriendRelation.objects.filter(
        id=relation_id,
        addressee=request.current_user,
        status="pending"
    ).first()
    if not relation:
        return JsonResponse({"success": False, "msg": "好友申请不存在或已处理"})
    if action == "accept":
        relation.status = "accepted"
        msg = "已通过好友申请"
    elif action == "reject":
        relation.status = "rejected"
        msg = "已拒绝好友申请"
    else:
        return JsonResponse({"success": False, "msg": "操作类型错误"})
    relation.save(update_fields=["status", "updated_at"])
    return JsonResponse({"success": True, "msg": msg})

@csrf_exempt
@login_required
def delete_friend(request, user_id):
    if request.method != "DELETE":
        return JsonResponse({"success": False, "msg": "仅支持DELETE"}, status=405)
    ensure_friend_relation_table()
    relation = models.FriendRelation.objects.filter(
        status="accepted"
    ).filter(
        Q(requester=request.current_user, addressee_id=user_id) |
        Q(addressee=request.current_user, requester_id=user_id)
    ).first()
    if not relation:
        return JsonResponse({"success": False, "msg": "好友关系不存在"})
    relation.delete()
    return JsonResponse({"success": True, "msg": "好友已删除"})

@csrf_exempt
@login_required
def friend_settings(request):
    if request.method == "GET":
        return JsonResponse({
            "success": True,
            "allow_friend_requests": bool(request.current_user.allow_friend_requests)
        })
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持GET或POST"}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
    allow = bool(data.get("allow_friend_requests", True))
    request.current_user.allow_friend_requests = allow
    request.current_user.save(update_fields=["allow_friend_requests"])
    return JsonResponse({
        "success": True,
        "msg": "好友申请设置已更新",
        "allow_friend_requests": allow
    })

@csrf_exempt
@login_required
def friend_messages(request, user_id):
    ensure_friend_relation_table()
    user = request.current_user
    friend = models.User.objects.filter(id=user_id, is_deleted=False).first()
    if not friend:
        return JsonResponse({"success": False, "msg": "好友不存在"}, status=404)
    if not accepted_relation_between_users(user.id, friend.id):
        return JsonResponse({"success": False, "msg": "只有好友之间可以聊天"}, status=403)

    if request.method == "GET":
        models.FriendMessage.objects.filter(
            sender=friend,
            receiver=user,
            is_read=False
        ).update(is_read=True)
        records = models.FriendMessage.objects.filter(
            Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
        ).order_by("created_at", "id")[:300]
        return JsonResponse({
            "success": True,
            "friend": serialize_friend_user(friend, accepted_relation_between_users(user.id, friend.id), user),
            "messages": [
                {
                    "id": item.id,
                    "sender_id": item.sender_id,
                    "receiver_id": item.receiver_id,
                    "content": item.content,
                    "mine": item.sender_id == user.id,
                    "is_read": item.is_read,
                    "created_at": item.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for item in records
            ]
        })

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = str(data.get("content", "")).strip()
        except (TypeError, json.JSONDecodeError):
            return JsonResponse({"success": False, "msg": "请求格式错误"}, status=400)
        if not content:
            return JsonResponse({"success": False, "msg": "消息内容不能为空"})
        if len(content) > 500:
            return JsonResponse({"success": False, "msg": "消息内容不能超过500字"})
        message = models.FriendMessage.objects.create(
            sender=user,
            receiver=friend,
            content=content,
            is_read=False
        )
        return JsonResponse({
            "success": True,
            "msg": "消息已发送",
            "message": {
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "content": message.content,
                "mine": True,
                "is_read": False,
                "created_at": message.created_at.strftime("%Y-%m-%d %H:%M")
            }
        })

    return JsonResponse({"success": False, "msg": "仅支持GET或POST"}, status=405)

@login_required
def notifications(request):
    finish_expired_competitions()
    user = request.current_user
    ensure_friend_relation_table()
    messages = []
    for competition in models.Competition.objects.filter(organizer=user, status=4).order_by("-created_at"):
        messages.append({
            "id": f"competition-rejected-{competition.id}",
            "type": "赛事审核",
            "title": f"公开赛「{competition.title}」被驳回",
            "content": competition.reject_reason or "赛事审核未通过，请修改后重新提交。",
            "competition_id": competition.id,
            "created_at": competition.created_at.strftime("%Y-%m-%d %H:%M")
        })
    rejected_registrations = models.Registration.objects.filter(
        player=user,
        review_status=2
    ).select_related("competition").order_by("-registration_time")
    for registration in rejected_registrations:
        messages.append({
            "id": f"registration-rejected-{registration.id}",
            "type": "报名结果",
            "title": f"参加「{registration.competition.title}」失败",
            "content": registration.audit_remark or "你的报名未通过审核。",
            "competition_id": registration.competition_id,
            "created_at": registration.registration_time.strftime("%Y-%m-%d %H:%M")
        })
    incoming_requests = models.FriendRelation.objects.filter(
        addressee=user,
        status="pending"
    ).select_related("requester").order_by("-created_at")
    for relation in incoming_requests:
        requester_name = relation.requester.nickname or relation.requester.username
        messages.append({
            "id": f"friend-request-{relation.id}",
            "type": "好友申请",
            "title": f"{requester_name} 想添加你为好友",
            "content": "可以在这里直接通过或拒绝，也可以进入好友系统查看。",
            "friend_relation_id": relation.id,
            "action_required": True,
            "created_at": relation.created_at.strftime("%Y-%m-%d %H:%M")
        })
    accepted_requests = models.FriendRelation.objects.filter(
        requester=user,
        status="accepted"
    ).select_related("addressee").order_by("-updated_at")[:10]
    for relation in accepted_requests:
        friend_name = relation.addressee.nickname or relation.addressee.username
        messages.append({
            "id": f"friend-accepted-{relation.id}",
            "type": "好友通知",
            "title": f"{friend_name} 已通过你的好友申请",
            "content": "现在可以在好友系统中查看对方。",
            "friend_relation_id": relation.id,
            "created_at": relation.updated_at.strftime("%Y-%m-%d %H:%M")
        })
    unread_messages = models.FriendMessage.objects.filter(
        receiver=user,
        is_read=False
    ).select_related("sender").order_by("-created_at")
    unread_by_sender = {}
    for item in unread_messages:
        if item.sender_id not in unread_by_sender:
            unread_by_sender[item.sender_id] = {"sender": item.sender, "count": 0, "latest": item}
        unread_by_sender[item.sender_id]["count"] += 1
    for info in unread_by_sender.values():
        sender_name = info["sender"].nickname or info["sender"].username
        messages.append({
            "id": f"friend-message-{info['sender'].id}",
            "type": "好友消息",
            "title": f"{sender_name} 发来 {info['count']} 条新消息",
            "content": info["latest"].content,
            "friend_user_id": info["sender"].id,
            "created_at": info["latest"].created_at.strftime("%Y-%m-%d %H:%M")
        })
    messages.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return JsonResponse({"success": True, "messages": messages})

@csrf_exempt
@role_required("ADMIN")
def admin_stats(request):
    finish_expired_competitions()
    return JsonResponse({
        "success": True,
        "data": {
            "totalUsers": models.User.objects.count(),
            "runningEvents": models.Competition.objects.filter(status=2).count(),
            "pendingCount": models.Competition.objects.filter(status=0).count(),
            "rejectedCount": models.Competition.objects.filter(status=4).count(),
        }
    })

