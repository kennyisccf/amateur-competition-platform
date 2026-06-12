"""
URL configuration for amateur_competition_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app1 import views
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.conf import settings
from django.conf.urls.static import static
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})
urlpatterns = [
    #path("admin/", admin.site.urls),
    path('api/login/', views.login, name='login'),
    path('api/login-captcha/', views.login_captcha, name='login_captcha'),
    path('api/logout/', views.logout, name='logout'),
    path('api/register/', views.register, name='register'),
    path('api/upload/competition_thumbnail/', views.upload_competition_thumbnail),
    path('api/competitions/',views.competition_list, name='competition_list'),
    path('api/competition/<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('api/user/', views.user_detail, name="user_detail"),
    path('api/update_user/', views.update_user, name='update_user'),
    path('api/register_competition/', views.register_competition, name='register_competition'),
    path('api/create_competition/',views.create_competition,name='create_competition'),
    path('api/admin/pending_competitions/', views.pending_competitions, name='pending_competitions'),
    path('api/admin/review_competition/', views.review_competition, name='review_competition'),
    path('api/my_competitions/',views.my_competitions),
    path('api/competitions/<int:competition_id>/delete/',views.delete_competition),
    path('api/competitions/<int:competition_id>/update/',views.update_competition),
    path('api/competitions/<int:competition_id>/registrations/',views.competition_registrations),
    path('api/competitions/<int:competition_id>/bracket/', views.competition_bracket),
    path('api/my_registrations/',views.my_registrations),
    path('api/notifications/', views.notifications),
    path('api/friends/', views.friends),
    path('api/friends/search/', views.friend_search),
    path('api/friends/request/', views.send_friend_request),
    path('api/friends/respond/', views.respond_friend_request),
    path('api/friends/settings/', views.friend_settings),
    path('api/friends/<int:user_id>/messages/', views.friend_messages),
    path('api/friends/<int:user_id>/delete/', views.delete_friend),
    path('api/registrations/visibility/', views.update_registration_visibility),
    path("api/cancel_registration/",views.cancel_registration),
    path('api/approve_registration/',views.approve_registration),
    path('api/reject_registration/',views.reject_registration),
    path('api/registrations/status/', views.update_registration_status),
    path('api/admin/force_registration/', views.admin_force_registration),
    path('api/admin/registrations/<int:registration_id>/delete/', views.admin_delete_registration),
    path('api/competitions/<int:competition_id>/status/', views.update_competition_status),
    path('api/record_result/', views.record_result),
    path('api/admin/users/', views.admin_users),
    path('api/admin/users/create/', views.admin_create_user),
    path('api/admin/users/bulk_create/', views.admin_bulk_create_users),
    path('api/admin/competitions/bulk_add_users/', views.admin_bulk_force_registration),
    path('api/admin/competitions/bulk_create/', views.admin_bulk_create_competitions),
    path('api/admin/competitions/bulk_delete/', views.admin_bulk_delete_competitions),
    path('api/admin/users/bulk_delete/', views.admin_bulk_delete_users),
    path('api/admin/users/<int:user_id>/status/', views.toggle_user_status),
    path('api/admin/users/<int:user_id>/delete/', views.admin_delete_user),
    path('api/admin/audit_records/', views.audit_records),
    path('api/admin/stats/', views.admin_stats),
    path('csrf/', get_csrf_token, name = 'get_csrf_token'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
