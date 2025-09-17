"""
API URL patterns for REST API endpoints
"""
from django.urls import path, include
from . import api_views

# API URL patterns
api_urlpatterns = [
    # Authentication endpoints
    path('auth/login/', api_views.api_login, name='api_login'),
    path('auth/logout/', api_views.api_logout, name='api_logout'),
    
    # Student endpoints
    path('students/', api_views.api_students_list, name='api_students_list'),
    path('students/<int:student_id>/', api_views.api_student_detail, name='api_student_detail'),
    
    # Faculty endpoints
    path('faculty/', api_views.api_faculty_list, name='api_faculty_list'),
    
    # Achievement endpoints
    path('achievements/', api_views.api_achievements_list, name='api_achievements_list'),
    
    # Analytics endpoints
    path('analytics/dashboard/', api_views.api_analytics_dashboard, name='api_analytics_dashboard'),
    
    # Notification endpoints
    path('notifications/', api_views.api_notifications_list, name='api_notifications_list'),
    path('notifications/<int:notification_id>/read/', api_views.api_notification_mark_read, name='api_notification_mark_read'),
    
    # Documentation and health check
    path('docs/', api_views.api_documentation, name='api_documentation'),
    path('health/', api_views.api_health_check, name='api_health_check'),
]

urlpatterns = [
    # API endpoints
    path('api/', include(api_urlpatterns)),
]