from django.db import models

# Create your models here.
#python manage.py makemigrations
#python manage.py migrate
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        db_table = 'user'
        managed = False


class Competition(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    description = models.TextField(default='', null=True, blank=True, max_length=100)
    type = models.CharField(max_length=10)  # PUBLIC PRIVATE
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, db_column='organizer_id')
    status = models.IntegerField(default=0)  # 0待审核 1报名中 2进行中 3已结束 4驳回
    max_participants = models.IntegerField(default=100)
    current_participants = models.IntegerField(default=0)
    reward_points = models.IntegerField(default=100)
    reward = models.TextField(default='', null=True, blank=True, max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(max_length=50, null=True, blank=True)
    reject_reason = models.CharField( max_length=255,null=True,blank=True)
    class Meta:
        db_table = 'competition'
        managed = False


class Registration(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, db_column='player_id')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column='competition_id')
    status = models.CharField(max_length=20, default='pending')  # pending ongoing finished
    review_status = models.IntegerField(default=0) #0未审核 1通过 2未通过
    final_score = models.CharField(max_length=50, null=True, blank=True, default='')
    final_rank = models.IntegerField(default=0, null=True, blank=True)
    earned_points = models.IntegerField(default=0, null=True, blank=True)
    audit_remark = models.CharField(max_length=255, null=True, blank=True)
    registration_time = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        db_table = 'registration'
        unique_together = (('player', 'competition'),)
        managed = False

class Point_history(models.Model):
    username = models.CharField(max_length=50)
    change_amount = models.IntegerField(default=0)
    reason = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'point_history'
        unique_together = (('username', 'time'),)
        managed = False


class AuditRecord(models.Model):
    competition = models.ForeignKey(Competition,on_delete=models.CASCADE)
    action = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "audit_record"