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
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=10)  # PUBLIC PRIVATE
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, db_column='organizer_id')
    status = models.IntegerField(default=0)  # 0待审核 1报名中 2进行中 3已结束
    max_participants = models.IntegerField(default=100)
    current_participants = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'competition'
        managed = False


class Registration(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, db_column='player_id')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, db_column='competition_id')
    status = models.IntegerField(default=0)  # 0审核中 1报名成功 2已驳回
    audit_remark = models.CharField(max_length=255, null=True, blank=True)
    registration_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'registration'
        unique_together = (('player', 'competition'),)
        managed = False