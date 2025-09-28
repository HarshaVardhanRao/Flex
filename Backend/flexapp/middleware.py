"""
Middleware for Role-based Access Control, Security, and Audit Logging
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.db import models
import json
import time
from datetime import timedelta
from .models import AuditLog, SecurityLog, UserSession, Role, UserRole
from django.contrib.contenttypes.models import ContentType


class SecurityMiddleware(MiddlewareMixin):
    """Comprehensive security middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming requests for security checks"""
        # Skip security checks for certain paths
        skip_paths = ['/static/', '/media/', '/admin/jsi18n/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Log suspicious activity
        self._check_suspicious_activity(request)
        
        # Update session activity
        if request.user.is_authenticated:
            self._update_session_activity(request)
        
        return None
    
    def _check_suspicious_activity(self, request):
        """Check for suspicious activity patterns"""
        suspicious_indicators = [
            # Multiple failed login attempts
            'too many failed logins',
            # Unusual request patterns
            'rapid successive requests',
            # Suspicious user agents
            'bot patterns in user agent',
        ]
        
        # Check for rapid requests (basic rate limiting)
        if hasattr(request, 'session'):
            last_request_time = request.session.get('last_request_time', 0)
            current_time = time.time()
            
            if current_time - last_request_time < 0.5:  # Less than 500ms between requests
                try:
                    # Handle user instance properly for SecurityLog
                    user_for_log = None
                    if request.user.is_authenticated:
                        # Skip SecurityLog creation for custom user models to avoid conflicts
                        # The custom user models (student, Faculty) don't work directly with SecurityLog
                        # This is a design limitation that should be addressed in the future
                        pass
                    
                    # Only create SecurityLog for regular User instances
                    # SecurityLog.objects.create(
                    #     user=user_for_log,
                    #     event_type='suspicious_activity',
                    #     description='Rapid successive requests detected',
                    #     ip_address=self._get_client_ip(request),
                    #     user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    #     request_path=request.path,
                    #     request_method=request.method,
                    #     severity='medium'
                    # )
                except Exception as e:
                    # Log the error but don't break the request
                    import logging
                    logging.error(f"Error creating SecurityLog: {e}")
            
            request.session['last_request_time'] = current_time
    
    def _update_session_activity(self, request):
        """Update user session activity"""
        session_key = request.session.session_key
        if session_key and hasattr(request.user, 'pk') and request.user.pk:
            try:
                # Ensure request.user is a proper User instance, not a string
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                if isinstance(request.user, str):
                    # If user is a string, try to get the actual user object
                    try:
                        user_obj = User.objects.get(username=request.user)
                    except User.DoesNotExist:
                        return  # Skip if user doesn't exist
                else:
                    user_obj = request.user
                
                user_session = UserSession.objects.get(
                    user=user_obj,
                    session_key=session_key,
                    is_active=True
                )
                user_session.last_activity = timezone.now()
                user_session.save(update_fields=['last_activity'])
            except UserSession.DoesNotExist:
                # Create new session record
                try:
                    UserSession.objects.create(
                        user=user_obj,
                        session_key=session_key,
                        ip_address=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        device_info=self._extract_device_info(request)
                    )
                except Exception as e:
                    # Handle any errors in session creation
                    pass
            except Exception as e:
                # Handle any other errors in session update
                pass
    
    def _get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _extract_device_info(self, request):
        """Extract device information from user agent"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        # Basic device detection (can be enhanced with user-agents library)
        device_info = {
            'user_agent': user_agent,
            'is_mobile': 'Mobile' in user_agent or 'Android' in user_agent,
            'is_tablet': 'Tablet' in user_agent or 'iPad' in user_agent,
            'browser': self._detect_browser(user_agent),
        }
        return device_info
    
    def _detect_browser(self, user_agent):
        """Basic browser detection"""
        if 'Chrome' in user_agent:
            return 'Chrome'
        elif 'Firefox' in user_agent:
            return 'Firefox'
        elif 'Safari' in user_agent:
            return 'Safari'
        elif 'Edge' in user_agent:
            return 'Edge'
        else:
            return 'Unknown'


class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to automatically log user activities"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Store request start time for performance tracking"""
        request._audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log the request/response after processing"""
        # Skip logging for static files and certain paths
        skip_paths = ['/static/', '/media/', '/admin/jsi18n/', '/favicon.ico']
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        # Only log significant actions or errors
        if self._should_log_request(request, response):
            self._create_audit_log(request, response)
        
        return response
    
    def _should_log_request(self, request, response):
        """Determine if request should be logged"""
        # Log all POST, PUT, DELETE requests (data modifications)
        if request.method in ['POST', 'PUT', 'DELETE']:
            return True
        
        # Log authentication related requests
        auth_paths = ['/login', '/logout', '/api/login/', '/api/logout/']
        if any(request.path.startswith(path) for path in auth_paths):
            return True
        
        # Log error responses
        if response.status_code >= 400:
            return True
        
        # Log admin actions
        if request.path.startswith('/admin/'):
            return True
        
        # Log API requests
        if request.path.startswith('/api/'):
            return True
        
        return False
    
    def _create_audit_log(self, request, response):
        """Create audit log entry"""
        try:
            action_type = self._determine_action_type(request, response)
            description = self._generate_description(request, response, action_type)
            risk_level = self._assess_risk_level(request, response)
            
            # Extract request data (be careful with sensitive data)
            request_data = {}
            if hasattr(request, 'POST') and request.POST:
                request_data = {k: v for k, v in request.POST.items() 
                              if not any(sensitive in k.lower() for sensitive in ['password', 'token', 'key'])}
            
            # Skip AuditLog creation for custom user models to avoid conflicts
            # Similar issue as SecurityLog - custom user models don't work directly
            # AuditLog.objects.create(
            #     user=request.user if request.user.is_authenticated else None,
            #     action_type=action_type,
            #     description=description,
            #     ip_address=AuditLog.get_client_ip(request),
            #     user_agent=request.META.get('HTTP_USER_AGENT', ''),
            #     request_path=request.path,
            #     request_method=request.method,
            #     risk_level=risk_level,
            #     additional_data={
            #         'response_status': response.status_code,
            #         'request_data': request_data,
            #         'processing_time': time.time() - getattr(request, '_audit_start_time', 0),
            #     }
            # )
        except Exception as e:
            # Don't let audit logging break the application
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create audit log: {e}")
    
    def _determine_action_type(self, request, response):
        """Determine the type of action based on request"""
        path = request.path.lower()
        method = request.method
        
        # Authentication actions
        if 'login' in path:
            return 'user_login' if response.status_code < 400 else 'failed_login'
        elif 'logout' in path:
            return 'user_logout'
        
        # Data modification actions
        if method == 'POST':
            if 'achievement' in path:
                return 'achievement_created'
            elif 'project' in path:
                return 'project_created'
            elif 'certificate' in path:
                return 'certificate_uploaded'
            else:
                return 'data_created'
        elif method == 'PUT':
            return 'data_updated'
        elif method == 'DELETE':
            return 'data_deleted'
        
        # Export actions
        if 'export' in path or 'download' in path:
            return 'data_exported'
        
        # API access
        if path.startswith('/api/'):
            return 'api_access'
        
        return 'system_access'
    
    def _generate_description(self, request, response, action_type):
        """Generate human-readable description"""
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        path = request.path
        method = request.method
        status = response.status_code
        
        return f"{user} performed {action_type} on {path} ({method}) - Status: {status}"
    
    def _assess_risk_level(self, request, response):
        """Assess risk level of the action"""
        # High risk actions
        if request.method in ['DELETE']:
            return 'high'
        
        # Failed authentication
        if response.status_code == 401:
            return 'medium'
        
        # Admin actions
        if request.path.startswith('/admin/'):
            return 'medium'
        
        # Data export
        if 'export' in request.path or 'download' in request.path:
            return 'medium'
        
        # Error responses
        if response.status_code >= 500:
            return 'high'
        elif response.status_code >= 400:
            return 'medium'
        
        return 'low'


class RoleBasedAccessMiddleware(MiddlewareMixin):
    """Middleware to enforce role-based access control"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Check user roles and permissions for the requested resource"""
        # Skip for certain paths
        skip_paths = ['/static/', '/media/', '/login/', '/logout/', '/admin/login/', '/admin/jsi18n/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Allow anonymous access to public paths (including root path)
        public_paths = ['/api/overview/', '/', '/api/health/', '/api/docs/']
        if request.path in public_paths:
            return None
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            if request.path.startswith('/api/'):
                return JsonResponse({'error': 'Authentication required'}, status=401)
            # Don't redirect from root path to avoid loops
            if request.path != '/':
                return redirect('login')
        
        # Check role-based permissions for authenticated users
        elif not self._check_access_permission(request):
            # Log permission denied - DISABLED due to custom user model conflicts
            # try:
            #     if request.user.is_authenticated:
            #         # Get the proper user instance for AuditLog
            #         user_for_audit = request.user if hasattr(request.user, '_meta') and request.user._meta.model_name == 'user' else None
            #         
            #         AuditLog.log_action(
            #             user=user_for_audit,
            #             action_type='permission_denied',
            #             description=f"Access denied to {request.path} for user: {request.user.username}",
            #             request=request,
            #             risk_level='medium'
            #         )
            # except Exception as e:
            #     # Don't let audit logging break the application
            #     import logging
            #     logger = logging.getLogger(__name__)
            #     logger.error(f"Failed to create audit log for permission denied: {e}")
            
            
            if request.path.startswith('/api/'):
                return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            else:
                messages.error(request, 'You do not have permission to access this resource.')
                # Don't redirect to dashboard if we're already there
                if request.path != '/dashboard':
                    return redirect('dashboard')
        
        return None
    
    def _check_access_permission(self, request):
        """Check if user has permission to access the requested resource"""
        user = request.user
        path = request.path
        
        # Superuser has access to everything
        if user.is_superuser:
            return True
        
        # Get user's roles
        user_roles = UserRole.objects.filter(
            user=user,
            is_active=True,
            start_date__lte=timezone.now()
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
        )
        
        # Check path-based permissions
        permission_map = {
            '/admin/': ['super_admin', 'admin'],
            '/faculty/': ['faculty', 'coordinator', 'hod', 'admin'],
            '/compliance/': ['admin', 'hod', 'coordinator'],
            '/export/': ['faculty', 'admin'],
            '/approval/': ['faculty', 'coordinator', 'hod'],
        }
        
        for path_prefix, required_roles in permission_map.items():
            if path.startswith(path_prefix):
                user_role_types = [ur.role.role_type for ur in user_roles]
                if not any(role_type in required_roles for role_type in user_role_types):
                    return False
                break
        
        # Additional permission checks based on user type
        user_type = getattr(user, 'type', lambda: 'unknown')()
        
        if user_type == 'student':
            # Students can only access their own data
            if 'profile' in path and '/student/' in path:
                # Extract student ID from path and check ownership
                pass  # Implement specific student access checks
        
        return True


class SessionTimeoutMiddleware(MiddlewareMixin):
    """Middleware to handle session timeouts"""
    
    def process_request(self, request):
        """Check for session timeout"""
        if not request.user.is_authenticated:
            return None
        
        # Check session timeout
        last_activity = request.session.get('last_activity')
        if last_activity:
            inactive_duration = timezone.now().timestamp() - last_activity
            max_inactive = getattr(settings, 'SESSION_TIMEOUT', 3600)  # 1 hour default
            
            if inactive_duration > max_inactive:
                # Log session timeout - DISABLED due to custom user model conflicts
                # try:
                #     if request.user.is_authenticated:
                #         # Get the proper user instance for AuditLog
                #         user_for_audit = request.user if hasattr(request.user, '_meta') and request.user._meta.model_name == 'user' else None
                #         
                #         AuditLog.log_action(
                #             user=user_for_audit,
                #             action_type='session_expired',
                #             description=f'Session expired due to inactivity for user: {request.user.username}',
                #             request=request
                #         )
                # except Exception as e:
                #     # Don't let audit logging break the application
                #     import logging
                #     logger = logging.getLogger(__name__)
                #     logger.error(f"Failed to create audit log for session timeout: {e}")
                
                # Mark session as inactive
                session_key = request.session.session_key
                if session_key:
                    UserSession.objects.filter(
                        session_key=session_key
                    ).update(
                        is_active=False,
                        logout_time=timezone.now()
                    )
                
                logout(request)
                # Check if messages framework is available before using it
                try:
                    messages.warning(request, 'Your session has expired due to inactivity. Please log in again.')
                except Exception:
                    # Fallback if messages framework is not ready
                    pass
                return redirect('login')
        
        # Update last activity
        request.session['last_activity'] = timezone.now().timestamp()
        return None