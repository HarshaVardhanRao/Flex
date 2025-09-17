"""
Notification Service for handling different delivery channels
"""
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
# from celery import shared_task  # Optional: for async processing
from typing import List, Dict, Optional

from .models import (
    EnhancedNotification, NotificationTemplate, NotificationPreference,
    AuditLog
)


class NotificationService:
    """
    Service class for handling notifications across multiple channels
    """
    
    def __init__(self):
        self.email_backend = EmailNotificationBackend()
        self.sms_backend = SMSNotificationBackend()
        self.push_backend = PushNotificationBackend()
        self.in_app_backend = InAppNotificationBackend()
    
    def send_notification(
        self,
        recipients: List[User],
        notification_type: str,
        title: str,
        message: str,
        template_name: Optional[str] = None,
        context: Optional[Dict] = None,
        channels: Optional[List[str]] = None,
        priority: str = 'medium',
        action_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, List[str]]:
        """
        Send notification to multiple recipients across multiple channels
        
        Returns:
            Dict with successful and failed deliveries per channel
        """
        if not recipients:
            return {'success': [], 'failed': []}
        
        # Default channels if not specified
        if channels is None:
            channels = ['in_app', 'email']
        
        # Prepare context for template rendering
        if context is None:
            context = {}
        
        context.update({
            'title': title,
            'message': message,
            'timestamp': timezone.now(),
            'action_url': action_url
        })
        
        results = {'success': [], 'failed': []}
        
        # Send to each channel
        for channel in channels:
            try:
                if channel == 'email':
                    result = self._send_email_notifications(
                        recipients, notification_type, title, message,
                        template_name, context, priority, action_url, metadata
                    )
                elif channel == 'sms':
                    result = self._send_sms_notifications(
                        recipients, title, message, priority
                    )
                elif channel == 'push':
                    result = self._send_push_notifications(
                        recipients, title, message, priority, action_url
                    )
                elif channel == 'in_app':
                    result = self._send_in_app_notifications(
                        recipients, notification_type, title, message,
                        priority, action_url, metadata
                    )
                else:
                    continue
                
                results['success'].extend(result.get('success', []))
                results['failed'].extend(result.get('failed', []))
                
            except Exception as e:
                # Log the error
                AuditLog.log_action(
                    user=None,
                    action_type='notification_error',
                    description=f'Error sending {channel} notification: {str(e)}',
                    risk_level='medium'
                )
                results['failed'].extend([f'{channel}:{user.username}' for user in recipients])
        
        return results
    
    def _send_email_notifications(
        self, recipients, notification_type, title, message,
        template_name, context, priority, action_url, metadata
    ):
        """Send email notifications"""
        results = {'success': [], 'failed': []}
        
        for user in recipients:
            try:
                # Check user's email notification preferences
                pref = NotificationPreference.objects.filter(
                    user=user,
                    notification_type=notification_type
                ).first()
                
                if pref and not pref.email_enabled:
                    continue
                
                # Get email template
                template = None
                if template_name:
                    template = NotificationTemplate.objects.filter(
                        name=template_name,
                        channel='email',
                        is_active=True
                    ).first()
                
                # Prepare email content
                if template:
                    email_subject = template.render_subject(context)
                    email_body = template.render_body(context)
                else:
                    email_subject = title
                    email_body = message
                
                # Send email
                success = self.email_backend.send_email(
                    recipient=user.email,
                    subject=email_subject,
                    body=email_body,
                    html_body=template.render_body(context) if template else None
                )
                
                if success:
                    results['success'].append(f'email:{user.username}')
                else:
                    results['failed'].append(f'email:{user.username}')
                    
            except Exception as e:
                results['failed'].append(f'email:{user.username}')
        
        return results
    
    def _send_sms_notifications(self, recipients, title, message, priority):
        """Send SMS notifications"""
        results = {'success': [], 'failed': []}
        
        for user in recipients:
            try:
                # Check if user has phone number
                student = getattr(user, 'student', None)
                phone = getattr(student, 'phone', None) if student else None
                
                if not phone:
                    continue
                
                # Send SMS
                success = self.sms_backend.send_sms(
                    phone_number=phone,
                    message=f'{title}: {message}'
                )
                
                if success:
                    results['success'].append(f'sms:{user.username}')
                else:
                    results['failed'].append(f'sms:{user.username}')
                    
            except Exception as e:
                results['failed'].append(f'sms:{user.username}')
        
        return results
    
    def _send_push_notifications(self, recipients, title, message, priority, action_url):
        """Send push notifications"""
        results = {'success': [], 'failed': []}
        
        for user in recipients:
            try:
                # For now, we'll implement a basic push notification
                # In a real implementation, you'd integrate with services like FCM
                success = self.push_backend.send_push(
                    user=user,
                    title=title,
                    message=message,
                    action_url=action_url
                )
                
                if success:
                    results['success'].append(f'push:{user.username}')
                else:
                    results['failed'].append(f'push:{user.username}')
                    
            except Exception as e:
                results['failed'].append(f'push:{user.username}')
        
        return results
    
    def _send_in_app_notifications(
        self, recipients, notification_type, title, message,
        priority, action_url, metadata
    ):
        """Send in-app notifications"""
        results = {'success': [], 'failed': []}
        
        for user in recipients:
            try:
                # Create in-app notification
                notification = EnhancedNotification.objects.create(
                    recipient=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    action_url=action_url,
                    metadata=metadata or {}
                )
                
                results['success'].append(f'in_app:{user.username}')
                
            except Exception as e:
                results['failed'].append(f'in_app:{user.username}')
        
        return results


class EmailNotificationBackend:
    """Email notification backend"""
    
    def send_email(self, recipient: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email notification"""
        try:
            if html_body:
                # Send HTML email
                from django.core.mail import EmailMultiAlternatives
                
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient]
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
            else:
                # Send plain text email
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    fail_silently=False
                )
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False


class SMSNotificationBackend:
    """SMS notification backend using Twilio or similar service"""
    
    def __init__(self):
        # Configure your SMS service here
        self.api_key = getattr(settings, 'SMS_API_KEY', None)
        self.api_url = getattr(settings, 'SMS_API_URL', None)
    
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            if not self.api_key or not self.api_url:
                print("SMS service not configured")
                return False
            
            # Example implementation for a generic SMS API
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'to': phone_number,
                    'message': message
                },
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False


class PushNotificationBackend:
    """Push notification backend using FCM or similar service"""
    
    def __init__(self):
        self.fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', None)
    
    def send_push(self, user: User, title: str, message: str, action_url: str = None) -> bool:
        """Send push notification"""
        try:
            # This is a placeholder implementation
            # In a real app, you'd need to store device tokens and use FCM
            
            if not self.fcm_server_key:
                print("Push notification service not configured")
                return False
            
            # For demonstration, we'll just log the push notification
            print(f"Push notification sent to {user.username}: {title} - {message}")
            return True
            
        except Exception as e:
            print(f"Push notification failed: {e}")
            return False


class InAppNotificationBackend:
    """In-app notification backend (database storage)"""
    
    def send_notification(self, user: User, title: str, message: str, **kwargs) -> bool:
        """Create in-app notification"""
        try:
            EnhancedNotification.objects.create(
                recipient=user,
                title=title,
                message=message,
                **kwargs
            )
            return True
            
        except Exception as e:
            print(f"In-app notification failed: {e}")
            return False


# Async notification processing (can be enabled with Celery)
# @shared_task
def send_async_notification(
    recipient_ids: List[int],
    notification_type: str,
    title: str,
    message: str,
    template_name: str = None,
    context: Dict = None,
    channels: List[str] = None,
    priority: str = 'medium',
    action_url: str = None,
    metadata: Dict = None
):
    """
    Asynchronous task for sending notifications
    """
    try:
        recipients = User.objects.filter(id__in=recipient_ids)
        
        service = NotificationService()
        results = service.send_notification(
            recipients=recipients,
            notification_type=notification_type,
            title=title,
            message=message,
            template_name=template_name,
            context=context,
            channels=channels,
            priority=priority,
            action_url=action_url,
            metadata=metadata
        )
        
        # Log the results
        AuditLog.log_action(
            user=None,
            action_type='notification_sent',
            description=f'Sent notifications: {len(results["success"])} successful, {len(results["failed"])} failed',
            risk_level='low'
        )
        
        return results
        
    except Exception as e:
        # Log the error
        AuditLog.log_action(
            user=None,
            action_type='notification_error',
            description=f'Error in async notification task: {str(e)}',
            risk_level='high'
        )
        raise


# Utility functions for common notification patterns
def notify_achievement_approved(achievement):
    """Send notification when achievement is approved"""
    service = NotificationService()
    return service.send_notification(
        recipients=[achievement.rollno.user] if hasattr(achievement.rollno, 'user') else [],
        notification_type='achievement_approved',
        title='Achievement Approved',
        message=f'Your achievement "{achievement.title}" has been approved!',
        template_name='achievement_approved',
        context={'achievement': achievement},
        channels=['in_app', 'email'],
        priority='high',
        action_url=f'/achievements/{achievement.id}/'
    )


def notify_new_form_assigned(form, user):
    """Send notification when a new form is assigned"""
    service = NotificationService()
    return service.send_notification(
        recipients=[user],
        notification_type='form_assigned',
        title='New Form Assigned',
        message=f'A new form "{form.title}" has been assigned to you.',
        template_name='form_assigned',
        context={'form': form, 'user': user},
        channels=['in_app', 'email'],
        priority='medium',
        action_url=f'/forms/{form.id}/'
    )


def notify_system_maintenance(users, start_time, end_time):
    """Send system maintenance notification"""
    service = NotificationService()
    return service.send_notification(
        recipients=users,
        notification_type='system_maintenance',
        title='Scheduled System Maintenance',
        message=f'System maintenance is scheduled from {start_time} to {end_time}.',
        template_name='system_maintenance',
        context={
            'start_time': start_time,
            'end_time': end_time
        },
        channels=['in_app', 'email'],
        priority='high'
    )