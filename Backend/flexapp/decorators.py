"""
Decorators for Role-based Access Control and Security
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.conf import settings
from .models import UserRole, AuditLog, SecurityLog


def role_required(allowed_roles):
    """
    Decorator to check if user has any of the specified roles
    
    Usage:
    @role_required(['admin', 'faculty'])
    def some_view(request):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Superuser has access to everything
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Get user's active roles
            user_roles = UserRole.objects.filter(
                user=user,
                is_active=True,
                start_date__lte=timezone.now()
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
            ).select_related('role')
            
            user_role_types = [ur.role.role_type for ur in user_roles]
            
            # Check if user has any of the required roles
            if not any(role in allowed_roles for role in user_role_types):
                # Log permission denied
                AuditLog.log_action(
                    user=user,
                    action_type='permission_denied',
                    description=f"Access denied to {request.path}. Required roles: {allowed_roles}",
                    request=request,
                    risk_level='medium'
                )
                
                if request.content_type == 'application/json' or request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Insufficient permissions'}, status=403)
                else:
                    messages.error(request, 'You do not have permission to access this resource.')
                    return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission_codenames):
    """
    Decorator to check if user has specific permissions
    
    Usage:
    @permission_required(['view_student', 'change_student'])
    def some_view(request):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Superuser has all permissions
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check permissions through roles
            user_roles = UserRole.objects.filter(
                user=user,
                is_active=True,
                start_date__lte=timezone.now()
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
            ).select_related('role')
            
            # Collect all permissions from user's roles
            user_permissions = set()
            for user_role in user_roles:
                role_permissions = user_role.role.permissions.values_list('codename', flat=True)
                user_permissions.update(role_permissions)
            
            # Also check direct user permissions
            direct_permissions = user.user_permissions.values_list('codename', flat=True)
            user_permissions.update(direct_permissions)
            
            # Check if user has all required permissions
            required_perms = set(permission_codenames)
            if not required_perms.issubset(user_permissions):
                missing_perms = required_perms - user_permissions
                
                # Log permission denied
                AuditLog.log_action(
                    user=user,
                    action_type='permission_denied',
                    description=f"Access denied to {request.path}. Missing permissions: {list(missing_perms)}",
                    request=request,
                    risk_level='medium'
                )
                
                if request.content_type == 'application/json' or request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Insufficient permissions'}, status=403)
                else:
                    messages.error(request, 'You do not have permission to perform this action.')
                    return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def department_access_required(check_ownership=True):
    """
    Decorator to check if user has access to specific department data
    
    Usage:
    @department_access_required()
    def view_department_data(request, dept):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Superuser and admin have access to all departments
            if user.is_superuser or hasattr(user, 'is_admin') and user.is_admin:
                return view_func(request, *args, **kwargs)
            
            # Get requested department from URL parameters
            target_dept = kwargs.get('dept') or request.GET.get('dept')
            
            if check_ownership and target_dept:
                # Check if user belongs to the requested department
                user_dept = getattr(user, 'dept', None)
                
                # Also check role-based department access
                user_roles = UserRole.objects.filter(
                    user=user,
                    is_active=True,
                    start_date__lte=timezone.now()
                ).filter(
                    models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
                )
                
                role_departments = [ur.department for ur in user_roles if ur.department]
                
                if target_dept != user_dept and target_dept not in role_departments:
                    # Log unauthorized department access attempt
                    AuditLog.log_action(
                        user=user,
                        action_type='permission_denied',
                        description=f"Unauthorized department access attempt: {target_dept}",
                        request=request,
                        risk_level='high'
                    )
                    
                    if request.content_type == 'application/json' or request.path.startswith('/api/'):
                        return JsonResponse({'error': 'Access denied to this department'}, status=403)
                    else:
                        messages.error(request, 'You do not have access to this department data.')
                        return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def audit_action(action_type, description=None, risk_level='low'):
    """
    Decorator to automatically audit specific actions
    
    Usage:
    @audit_action('data_exported', 'Student data exported', 'medium')
    def export_students(request):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Execute the view function
            response = view_func(request, *args, **kwargs)
            
            # Create audit log after successful execution
            if hasattr(response, 'status_code') and response.status_code < 400:
                audit_description = description or f"Executed {view_func.__name__}"
                
                AuditLog.log_action(
                    user=request.user if request.user.is_authenticated else None,
                    action_type=action_type,
                    description=audit_description,
                    request=request,
                    risk_level=risk_level,
                    view_name=view_func.__name__
                )
            
            return response
        return wrapper
    return decorator


def rate_limit(max_requests=60, time_window=3600):  # 60 requests per hour by default
    """
    Simple rate limiting decorator
    
    Usage:
    @rate_limit(max_requests=100, time_window=3600)
    def api_endpoint(request):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Use a simple session-based rate limiting
            session_key = f"rate_limit_{view_func.__name__}"
            current_time = timezone.now().timestamp()
            
            # Get request history from session
            request_history = request.session.get(session_key, [])
            
            # Remove old requests outside the time window
            request_history = [req_time for req_time in request_history 
                             if current_time - req_time < time_window]
            
            # Check if rate limit exceeded
            if len(request_history) >= max_requests:
                # Log rate limit violation
                SecurityLog.objects.create(
                    user=request.user,
                    event_type='suspicious_activity',
                    description=f'Rate limit exceeded for {view_func.__name__}',
                    ip_address=AuditLog.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    request_path=request.path,
                    request_method=request.method,
                    severity='medium'
                )
                
                if request.content_type == 'application/json' or request.path.startswith('/api/'):
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'retry_after': time_window
                    }, status=429)
                else:
                    messages.warning(request, 'Too many requests. Please try again later.')
                    return redirect('dashboard')
            
            # Add current request to history
            request_history.append(current_time)
            request.session[session_key] = request_history
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def secure_view(require_https=True, check_referrer=True):
    """
    Security decorator for sensitive views
    
    Usage:
    @secure_view(require_https=True, check_referrer=True)
    def sensitive_view(request):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check HTTPS requirement
            if require_https and not request.is_secure() and not settings.DEBUG:
                return JsonResponse({'error': 'HTTPS required'}, status=400)
            
            # Check referrer for POST requests
            if check_referrer and request.method == 'POST':
                referrer = request.META.get('HTTP_REFERER', '')
                allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
                
                if referrer and not any(host in referrer for host in allowed_hosts):
                    # Log suspicious referrer
                    SecurityLog.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        event_type='suspicious_activity',
                        description=f'Suspicious referrer: {referrer}',
                        ip_address=AuditLog.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        request_path=request.path,
                        request_method=request.method,
                        severity='medium'
                    )
                    
                    return JsonResponse({'error': 'Invalid referrer'}, status=400)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_data_access(resource_type):
    """
    Decorator to log data access for compliance
    
    Usage:
    @log_data_access('student_records')
    def view_student_data(request, student_id):
        pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Log data access
            AuditLog.log_action(
                user=request.user if request.user.is_authenticated else None,
                action_type='data_access',
                description=f"Accessed {resource_type}: {request.path}",
                request=request,
                risk_level='low',
                resource_type=resource_type,
                request_params=kwargs
            )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Convenience decorators combining multiple checks
def admin_required(view_func):
    """Shortcut decorator for admin-only views"""
    return role_required(['admin', 'super_admin'])(view_func)


def faculty_required(view_func):
    """Shortcut decorator for faculty-only views"""
    return role_required(['faculty', 'coordinator', 'hod', 'admin'])(view_func)


def student_required(view_func):
    """Shortcut decorator for student-only views"""
    return role_required(['student'])(view_func)


def coordinator_required(view_func):
    """Shortcut decorator for coordinator-level access"""
    return role_required(['coordinator', 'hod', 'admin'])(view_func)