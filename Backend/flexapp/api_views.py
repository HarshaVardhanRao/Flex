"""
API Views for REST API endpoints with authentication and security
"""
import json
import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.serializers import serialize
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.conf import settings
from django.core.exceptions import ValidationError
from django.views.decorators.cache import cache_page
from functools import wraps

from .models import (
    student, Faculty, Projects, publications, Certificate, Achievement,
    AchievementCategory, AuditLog, SecurityLog, APIKey, EnhancedNotification
)
from .decorators import (
    role_required, permission_required, audit_action, rate_limit,
    secure_view, log_data_access
)


def api_key_required(view_func):
    """
    Decorator to require valid API key for API access
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')
        
        if not api_key:
            return JsonResponse({'error': 'API key required'}, status=401)
        
        try:
            api_key_obj = APIKey.objects.get(
                key=api_key,
                is_active=True,
                expires_at__gt=timezone.now()
            )
            
            # Update last used
            api_key_obj.last_used = timezone.now()
            api_key_obj.usage_count += 1
            api_key_obj.save()
            
            # Add API key info to request
            request.api_key = api_key_obj
            
            # Check rate limits
            if api_key_obj.has_exceeded_rate_limit():
                return JsonResponse({
                    'error': 'Rate limit exceeded for API key',
                    'limit': api_key_obj.rate_limit_per_hour,
                    'reset_time': (timezone.now() + timedelta(hours=1)).isoformat()
                }, status=429)
            
        except APIKey.DoesNotExist:
            # Log invalid API key attempt
            SecurityLog.objects.create(
                event_type='invalid_api_key',
                description=f'Invalid API key used: {api_key[:10]}...',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_path=request.path,
                request_method=request.method,
                severity='high'
            )
            return JsonResponse({'error': 'Invalid API key'}, status=401)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def jwt_required(view_func):
    """
    Decorator to require valid JWT token for API access
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'JWT token required'}, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            user_id = payload.get('user_id')
            if not user_id:
                raise jwt.InvalidTokenError('Invalid token payload')
            
            user = User.objects.get(id=user_id)
            request.user = user
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def paginate_response(request, queryset, serializer_func, page_size=20):
    """
    Helper function to paginate API responses
    """
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return {
        'data': [serializer_func(item) for item in page_obj],
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    }


# Authentication API endpoints
@csrf_exempt
@require_http_methods(["POST"])
@rate_limit(max_requests=10, time_window=900)  # 10 attempts per 15 minutes
def api_login(request):
    """
    API endpoint for user authentication
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            # Create JWT token
            payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            # Log successful login
            AuditLog.log_action(
                user=user,
                action_type='login',
                description='API login successful',
                request=request,
                risk_level='low'
            )
            
            return JsonResponse({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            })
        else:
            # Log failed login attempt
            SecurityLog.objects.create(
                event_type='failed_login',
                description=f'Failed API login attempt for username: {username}',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request_path=request.path,
                request_method=request.method,
                severity='medium'
            )
            
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def api_logout(request):
    """
    API endpoint for user logout
    """
    # Log logout
    AuditLog.log_action(
        user=request.user,
        action_type='logout',
        description='API logout',
        request=request,
        risk_level='low'
    )
    
    return JsonResponse({'message': 'Logged out successfully'})


# Student API endpoints
@api_key_required
@cache_page(60 * 5)  # Cache for 5 minutes
@log_data_access('student_list')
def api_students_list(request):
    """
    API endpoint to get list of students with filtering and pagination
    """
    # Get query parameters
    dept = request.GET.get('dept')
    year = request.GET.get('year')
    search = request.GET.get('search')
    page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 items per page
    
    # Build queryset
    queryset = student.objects.all()
    
    if dept:
        queryset = queryset.filter(dept=dept)
    if year:
        queryset = queryset.filter(year=year)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(rollno__icontains=search) |
            Q(email__icontains=search)
        )
    
    def serialize_student(student):
        return {
            'id': student.id,
            'rollno': student.rollno,
            'name': student.name,
            'email': student.email,
            'dept': student.dept,
            'year': student.year,
            'cgpa': float(student.cgpa) if student.cgpa else None,
            'phone': student.phone,
            'github_link': student.github_link,
            'created_at': student.created_at.isoformat() if hasattr(student, 'created_at') else None
        }
    
    response_data = paginate_response(request, queryset, serialize_student, page_size)
    return JsonResponse(response_data)


@api_key_required
@log_data_access('student_detail')
def api_student_detail(request, student_id):
    """
    API endpoint to get detailed student information
    """
    try:
        student_obj = student.objects.get(id=student_id)
        
        # Get related data
        projects = Projects.objects.filter(rollno=student_obj.rollno)
        publications_list = publications.objects.filter(rollno=student_obj.rollno)
        certificates = Certificate.objects.filter(rollno=student_obj.rollno)
        achievements = Achievement.objects.filter(rollno=student_obj.rollno)
        
        data = {
            'student': {
                'id': student_obj.id,
                'rollno': student_obj.rollno,
                'name': student_obj.name,
                'email': student_obj.email,
                'personal_email': student_obj.personal_email,
                'dept': student_obj.dept,
                'year': student_obj.year,
                'cgpa': float(student_obj.cgpa) if student_obj.cgpa else None,
                'phone': student_obj.phone,
                'date_of_birth': student_obj.date_of_birth.isoformat() if student_obj.date_of_birth else None,
                'github_link': student_obj.github_link,
                'linkedin_profile': student_obj.linkedin_profile,
                'portfolio_url': student_obj.portfolio_url,
                'guardian_info': student_obj.guardian_info,
                'address': student_obj.address,
                'career_interests': student_obj.career_interests,
                'skills': student_obj.skills,
                'extracurricular_activities': student_obj.extracurricular_activities
            },
            'projects': [{
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'github_link': p.github_link,
                'year': p.year,
                'sem': p.sem
            } for p in projects],
            'publications': [{
                'id': p.id,
                'title': p.title,
                'authors': p.authors,
                'journal': p.journal,
                'year': p.year,
                'doi': p.doi
            } for p in publications_list],
            'certificates': [{
                'id': c.id,
                'name': c.name,
                'issuer': c.issuer,
                'issue_date': c.issue_date.isoformat() if c.issue_date else None,
                'expiry_date': c.expiry_date.isoformat() if c.expiry_date else None,
                'certificate_url': c.certificate_url
            } for c in certificates],
            'achievements': [{
                'id': a.id,
                'title': a.title,
                'description': a.description,
                'category': a.category.name if a.category else None,
                'achievement_date': a.achievement_date.isoformat() if a.achievement_date else None,
                'level': a.level,
                'status': a.status
            } for a in achievements]
        }
        
        return JsonResponse(data)
        
    except student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)


# Faculty API endpoints
@api_key_required
@log_data_access('faculty_list')
def api_faculty_list(request):
    """
    API endpoint to get list of faculty
    """
    dept = request.GET.get('dept')
    page_size = min(int(request.GET.get('page_size', 20)), 100)
    
    queryset = Faculty.objects.all()
    if dept:
        queryset = queryset.filter(dept=dept)
    
    def serialize_faculty(faculty):
        return {
            'id': faculty.id,
            'name': faculty.name,
            'email': faculty.email,
            'dept': faculty.dept,
            'designation': faculty.designation,
            'phone': faculty.phone,
            'research_interests': faculty.research_interests
        }
    
    response_data = paginate_response(request, queryset, serialize_faculty, page_size)
    return JsonResponse(response_data)


# Achievement API endpoints
@api_key_required
@log_data_access('achievements')
def api_achievements_list(request):
    """
    API endpoint to get achievements with filtering
    """
    student_id = request.GET.get('student_id')
    category = request.GET.get('category')
    status = request.GET.get('status', 'approved')
    page_size = min(int(request.GET.get('page_size', 20)), 100)
    
    queryset = Achievement.objects.all()
    
    if student_id:
        queryset = queryset.filter(rollno__id=student_id)
    if category:
        queryset = queryset.filter(category__name=category)
    if status:
        queryset = queryset.filter(status=status)
    
    def serialize_achievement(achievement):
        return {
            'id': achievement.id,
            'title': achievement.title,
            'description': achievement.description,
            'student': {
                'id': achievement.rollno.id,
                'name': achievement.rollno.name,
                'rollno': achievement.rollno.rollno
            } if achievement.rollno else None,
            'category': achievement.category.name if achievement.category else None,
            'level': achievement.level,
            'achievement_date': achievement.achievement_date.isoformat() if achievement.achievement_date else None,
            'status': achievement.status,
            'approved_by': achievement.approved_by.get_full_name() if achievement.approved_by else None,
            'approved_at': achievement.approved_at.isoformat() if achievement.approved_at else None
        }
    
    response_data = paginate_response(request, queryset, serialize_achievement, page_size)
    return JsonResponse(response_data)


# Analytics API endpoints
@api_key_required
@cache_page(60 * 15)  # Cache for 15 minutes
def api_analytics_dashboard(request):
    """
    API endpoint for dashboard analytics
    """
    try:
        # Student statistics
        total_students = student.objects.count()
        students_by_dept = dict(
            student.objects.values('dept').annotate(count=Count('id')).values_list('dept', 'count')
        )
        students_by_year = dict(
            student.objects.values('year').annotate(count=Count('id')).values_list('year', 'count')
        )
        
        # Achievement statistics
        total_achievements = Achievement.objects.filter(status='approved').count()
        achievements_by_category = dict(
            Achievement.objects.filter(status='approved')
            .values('category__name')
            .annotate(count=Count('id'))
            .values_list('category__name', 'count')
        )
        
        # Performance statistics
        avg_cgpa_by_dept = dict(
            student.objects.exclude(cgpa__isnull=True)
            .values('dept')
            .annotate(avg_cgpa=Avg('cgpa'))
            .values_list('dept', 'avg_cgpa')
        )
        
        # Project statistics
        total_projects = Projects.objects.count()
        projects_by_year = dict(
            Projects.objects.values('year').annotate(count=Count('id')).values_list('year', 'count')
        )
        
        analytics_data = {
            'students': {
                'total': total_students,
                'by_department': students_by_dept,
                'by_year': students_by_year
            },
            'achievements': {
                'total': total_achievements,
                'by_category': achievements_by_category
            },
            'performance': {
                'avg_cgpa_by_department': {
                    dept: round(float(cgpa), 2) for dept, cgpa in avg_cgpa_by_dept.items()
                }
            },
            'projects': {
                'total': total_projects,
                'by_year': projects_by_year
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return JsonResponse(analytics_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Notification API endpoints
@api_key_required
@jwt_required
def api_notifications_list(request):
    """
    API endpoint to get user notifications
    """
    notifications = EnhancedNotification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:50]  # Last 50 notifications
    
    def serialize_notification(notification):
        return {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'metadata': notification.metadata
        }
    
    data = {
        'notifications': [serialize_notification(n) for n in notifications],
        'unread_count': notifications.filter(is_read=False).count()
    }
    
    return JsonResponse(data)


@csrf_exempt
@api_key_required
@jwt_required
@require_http_methods(["PATCH"])
def api_notification_mark_read(request, notification_id):
    """
    API endpoint to mark notification as read
    """
    try:
        notification = EnhancedNotification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({'message': 'Notification marked as read'})
        
    except EnhancedNotification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)


# API documentation endpoint
@api_key_required
def api_documentation(request):
    """
    API endpoint documentation
    """
    documentation = {
        'version': '1.0',
        'base_url': request.build_absolute_uri('/api/'),
        'authentication': {
            'api_key': 'Include X-API-Key header with your API key',
            'jwt_token': 'Include Authorization: Bearer <token> header for authenticated endpoints'
        },
        'endpoints': {
            'authentication': {
                'POST /api/auth/login/': 'Login and get JWT token',
                'POST /api/auth/logout/': 'Logout (requires JWT)'
            },
            'students': {
                'GET /api/students/': 'List students with pagination and filtering',
                'GET /api/students/{id}/': 'Get detailed student information'
            },
            'faculty': {
                'GET /api/faculty/': 'List faculty members'
            },
            'achievements': {
                'GET /api/achievements/': 'List achievements with filtering'
            },
            'analytics': {
                'GET /api/analytics/dashboard/': 'Get dashboard analytics data'
            },
            'notifications': {
                'GET /api/notifications/': 'Get user notifications (requires JWT)',
                'PATCH /api/notifications/{id}/read/': 'Mark notification as read (requires JWT)'
            }
        },
        'pagination': {
            'parameters': {
                'page': 'Page number (default: 1)',
                'page_size': 'Items per page (default: 20, max: 100)'
            }
        },
        'rate_limits': {
            'default': '60 requests per hour per API key',
            'authentication': '10 requests per 15 minutes per IP'
        }
    }
    
    return JsonResponse(documentation, json_dumps_params={'indent': 2})


# Health check endpoint (public - no authentication required)
@csrf_exempt
def api_health_check(request):
    """
    API health check endpoint - no authentication required
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0'
    })