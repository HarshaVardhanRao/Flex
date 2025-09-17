from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings
import json
import uuid
from datetime import datetime, timedelta

from django.db import models

# Role-based Access Control Models
class Role(models.Model):
    """Custom roles for fine-grained access control"""
    ROLE_TYPES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'), 
        ('coordinator', 'Department Coordinator'),
        ('hod', 'Head of Department'),
        ('admin', 'Administrator'),
        ('super_admin', 'Super Administrator'),
        ('guest', 'Guest User'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Department/Section specific roles
    department = models.CharField(max_length=20, blank=True, null=True)
    sections = models.CharField(max_length=100, blank=True, help_text="Comma-separated sections")
    
    # Role hierarchy level (1=highest, 10=lowest)
    hierarchy_level = models.IntegerField(default=5)
    
    class Meta:
        ordering = ['hierarchy_level', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_role_type_display()})"
    
    def has_permission(self, permission_codename):
        """Check if role has specific permission"""
        return self.permissions.filter(codename=permission_codename).exists()
    
    def get_all_permissions(self):
        """Get all permissions for this role"""
        return self.permissions.all()


class UserRole(models.Model):
    """Many-to-many relationship between users and roles with additional context"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    # Context-specific assignments
    department = models.CharField(max_length=20, blank=True, null=True)
    sections = models.CharField(max_length=100, blank=True, help_text="Comma-separated sections")
    academic_year = models.CharField(max_length=10, blank=True, null=True)
    
    # Time-bound roles
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    
    # Assignment details
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'role', 'department']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    def is_valid(self):
        """Check if role assignment is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class PermissionGroup(models.Model):
    """Logical grouping of permissions for easier management"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission)
    category = models.CharField(max_length=50, choices=[
        ('academic', 'Academic Management'),
        ('student', 'Student Management'),
        ('faculty', 'Faculty Management'),
        ('achievement', 'Achievement Management'),
        ('report', 'Report Generation'),
        ('system', 'System Administration'),
        ('security', 'Security & Audit'),
    ])
    
    def __str__(self):
        return self.name


# Session and Security Models
class UserSession(models.Model):
    """Track user sessions for security monitoring"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    device_info = models.JSONField(default=dict)
    
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_suspicious = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    
    def duration(self):
        """Calculate session duration"""
        end_time = self.logout_time or timezone.now()
        return end_time - self.login_time


class SecurityLog(models.Model):
    """Security event logging"""
    EVENT_TYPES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('logout', 'User Logout'),
        ('permission_denied', 'Permission Denied'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('password_change', 'Password Changed'),
        ('role_change', 'Role Assignment Changed'),
        ('data_export', 'Data Export'),
        ('admin_action', 'Administrative Action'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Request details
    request_path = models.CharField(max_length=255, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    
    # Response details
    response_status = models.IntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='low')
    
    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.created_at}"


class APIKey(models.Model):
    """API Key management for external integrations"""
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Permissions and restrictions
    permissions = models.ManyToManyField(Permission, blank=True)
    allowed_ips = models.TextField(blank=True, help_text="Comma-separated IP addresses")
    rate_limit = models.IntegerField(default=1000, help_text="Requests per hour")
    
    # Usage tracking
    total_requests = models.IntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def is_valid(self):
        """Check if API key is valid"""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    def increment_usage(self):
        """Increment usage counter"""
        self.total_requests += 1
        self.last_used = timezone.now()
        self.save(update_fields=['total_requests', 'last_used'])

class publications(models.Model):
    PUBLICATION_TYPE_CHOICES = [
        ('journal', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('book', 'Book/Book Chapter'),
        ('patent', 'Patent'),
        ('copyright', 'Copyright'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('published', 'Published'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('granted', 'Granted'),  # Useful for patents
    ]

    author = models.ForeignKey("Faculty", on_delete=models.CASCADE, related_name="publications")

    title = models.CharField(max_length=200)
    publication_type = models.CharField(max_length=30, choices=PUBLICATION_TYPE_CHOICES)
    publication_status = models.CharField(max_length=30, choices=STATUS_CHOICES)

    publication_date = models.DateField(null=True, blank=True)
    publication_area = models.CharField(max_length=100, blank=True)
    journal_or_publisher = models.CharField(max_length=200, blank=True)
    volume_or_edition = models.CharField(max_length=100, blank=True)

    abstract = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # For patents/copyrights
    registration_number = models.CharField(max_length=100, blank=True)
    granted_by = models.CharField(max_length=200, blank=True)

    # Link to full publication or proof
    link = models.URLField(blank=True)

    def __str__(self):
        return f"{self.author} - {self.title} ({self.publication_type})"

    def __str__(self):
        return self.title
class certifications(models.Model):
    author = models.ForeignKey("Faculty", on_delete=models.CASCADE, related_name="certifications")
    title = models.CharField(max_length=100)
    certification_date = models.DateField()
    certification_type = models.CharField(max_length=50)
    certification_link = models.URLField()
    certification_area = models.CharField(max_length=50)
    def __str__(self):
        return self.title

class Faculty(AbstractUser):
    SECTION_CHOICES = [
        ("A","A"),("B","B"),("C","C"),("D","D"),("E","E"),("F","F")
    ]
    DEPT_CHOICES = [
        ("CSE","CSE"),("CAI","CAI"),("CSD","CSD"),("CSM","CSM"),("CSC","CSC"),("CST","CST"),("ECE","ECE"),("EEE","EEE"),("CE","CE"),("ME","ME")
    ]
    dept= models.CharField(max_length=20, choices=DEPT_CHOICES, default="CSE")
    groups = models.ManyToManyField(Group, related_name="facultyGroups")
    user_permissions = models.ManyToManyField(Permission, related_name="facultyPermissions")
    default_year = models.IntegerField(default=None,null=True)
    default_section = models.CharField(max_length=10,choices=SECTION_CHOICES, default="A")

    def type(self):
        return "Faculty"


class Technology(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name



class student(AbstractUser):
    roll_no = models.CharField(max_length=12)
    leetcode_user = models.CharField(max_length=58,default="Username")
    DEPT_CHOICES = [
        ("CSE","CSE"),("CAI","CAI"),("CSD","CSD"),("CSM","CSM"),("CSC","CSC"),("CST","CST"),("ECE","ECE"),("EEE","EEE"),("CE","CE"),("ME","ME")
    ]
    SECTION_CHOICES = [
        ("A","A"),("B","B"),("C","C"),("D","D"),("E","E"),("F","F")
    ]
    dept= models.CharField(max_length=20, choices=DEPT_CHOICES, default="CSE")
    section = models.CharField(max_length=10,choices=SECTION_CHOICES, default="A")
    year = models.IntegerField(default=3)
    githublink = models.URLField(default=None,null=True)
    groups = models.ManyToManyField(Group, related_name="studentGroups")
    user_permissions = models.ManyToManyField(Permission, related_name="studentPermissions")
    phone = models.CharField(max_length=12, default="", null=True, blank=True)
    mentor = models.ForeignKey("Faculty", on_delete=models.SET_NULL, related_name="mentees", null=True, blank=True)
    
    # Enhanced Profile Fields
    personal_email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Academic Fields
    admission_year = models.IntegerField(blank=True, null=True)
    current_cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    total_credits = models.IntegerField(default=0)
    
    # Career & Skills
    career_interests = models.TextField(blank=True, null=True, help_text="Comma-separated interests")
    technical_skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    soft_skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    
    # Social Media & Professional Links
    linkedin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    
    # Status Fields
    is_active_student = models.BooleanField(default=True)
    graduation_status = models.CharField(max_length=20, choices=[
        ('current', 'Current Student'),
        ('graduated', 'Graduated'),
        ('dropped', 'Dropped Out')
    ], default='current')
    
    # Profile completion tracking
    profile_completion_percentage = models.IntegerField(default=0)
    last_profile_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name
    def type(self):
        return "student"
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        total_fields = 20  # Adjust based on required fields
        completed_fields = 0
        
        # Check mandatory fields
        if self.first_name: completed_fields += 1
        if self.last_name: completed_fields += 1
        if self.email: completed_fields += 1
        if self.phone: completed_fields += 1
        if self.dept: completed_fields += 1
        if self.year: completed_fields += 1
        if self.section: completed_fields += 1
        
        # Check optional fields
        if self.personal_email: completed_fields += 1
        if self.date_of_birth: completed_fields += 1
        if self.guardian_name: completed_fields += 1
        if self.guardian_phone: completed_fields += 1
        if self.address: completed_fields += 1
        if self.admission_year: completed_fields += 1
        if self.career_interests: completed_fields += 1
        if self.technical_skills: completed_fields += 1
        if self.soft_skills: completed_fields += 1
        if self.linkedin_url: completed_fields += 1
        if self.githublink: completed_fields += 1
        if self.leetcode_user and self.leetcode_user != "Username": completed_fields += 1
        if self.portfolio_url: completed_fields += 1
        
        percentage = (completed_fields / total_fields) * 100
        self.profile_completion_percentage = percentage
        return percentage


# Achievement Categories Model
class AchievementCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    points = models.IntegerField(default=10, help_text="Points awarded for this category")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Achievement Categories"
    
    def __str__(self):
        return self.name


# Enhanced Achievement Model
class Achievement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ]
    
    student = models.ForeignKey('student', on_delete=models.CASCADE, related_name='achievements')
    category = models.ForeignKey(AchievementCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval workflow
    submitted_by = models.ForeignKey('student', on_delete=models.CASCADE, related_name='submitted_achievements')
    reviewed_by = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, blank=True)
    approved_by = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_achievements')
    submission_date = models.DateTimeField(auto_now_add=True)
    review_date = models.DateTimeField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    
    # Comments and feedback
    faculty_comments = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # File attachments
    supporting_documents = models.FileField(upload_to='achievements/', null=True, blank=True)
    
    # Points and validation
    points_awarded = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.title}"


# Approval Workflow Model
class ApprovalWorkflow(models.Model):
    WORKFLOW_TYPES = [
        ('certificate', 'Certificate'),
        ('project', 'Project'),
        ('achievement', 'Achievement'),
        ('placement', 'Placement'),
        ('publication', 'Publication'),
    ]
    
    content_type = models.CharField(max_length=20, choices=WORKFLOW_TYPES)
    object_id = models.PositiveIntegerField()
    student = models.ForeignKey('student', on_delete=models.CASCADE)
    
    # Workflow steps
    submitted_at = models.DateTimeField(auto_now_add=True)
    initial_reviewer = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='initial_reviews')
    final_approver = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='final_approvals')
    
    # Status tracking
    current_status = models.CharField(max_length=20, choices=Achievement.STATUS_CHOICES, default='pending')
    workflow_history = models.JSONField(default=list)  # Track all status changes
    
    # Comments at each stage
    student_comments = models.TextField(blank=True, null=True)
    reviewer_comments = models.TextField(blank=True, null=True)
    approver_comments = models.TextField(blank=True, null=True)
    
    # Deadlines and SLA
    expected_review_date = models.DateTimeField(null=True, blank=True)
    expected_approval_date = models.DateTimeField(null=True, blank=True)
    is_overdue = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.content_type} - {self.student.username} - {self.current_status}"


# Academic Performance Model
class AcademicPerformance(models.Model):
    student = models.ForeignKey('student', on_delete=models.CASCADE, related_name='academic_records')
    semester = models.CharField(max_length=10)
    year = models.IntegerField()
    
    # Grade details
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    credits_earned = models.IntegerField(default=0)
    total_credits = models.IntegerField(default=0)
    
    # Attendance and discipline
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    disciplinary_actions = models.TextField(blank=True, null=True)
    
    # Rankings and achievements
    class_rank = models.IntegerField(null=True, blank=True)
    department_rank = models.IntegerField(null=True, blank=True)
    
    # Additional academic metrics
    subjects_passed = models.IntegerField(default=0)
    subjects_failed = models.IntegerField(default=0)
    backlogs = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'semester', 'year')
        ordering = ['-year', '-semester']
    
    def __str__(self):
        return f"{self.student.username} - {self.year} - {self.semester}"


# Notification System Model
class LeetCode(models.Model):
    TotalProblems = models.IntegerField(default=0)
    rollno = models.ForeignKey(student,on_delete=models.CASCADE, related_name="studentrollno")
    easy = models.IntegerField(default=0)
    medium = models.IntegerField(default=0)
    hard = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.rollno} - Total Problems Solved: {self.TotalProblems}"

from django.core.validators import MinValueValidator
from django.db import models

class Certificate(models.Model):
    rollno = models.ForeignKey(student, on_delete=models.CASCADE, related_name="certificates")

    # Core details
    source = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    certificate = models.FileField(upload_to='certificates/', null=True)

    # Extended Category Options
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('foreign_language', 'Foreign Language'),
        ('co_curricular', 'Co-Curricular'),
        ('extra_curricular', 'Extra-Curricular'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')

    # Year & Semester
    YEAR_AND_SEM_CHOICES = [
        ("I-I", "I-I"), ("I-II", "I-II"), ("II-I", "II-I"), ("II-II", "II-II"),
        ("III-I", "III-I"), ("III-II", "III-II"), ("IV-I", "IV-I"), ("IV-II", "IV-II")
    ]
    year_and_sem = models.CharField(max_length=10, choices=YEAR_AND_SEM_CHOICES)

    course_link = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Extended fields for better categorization
    domain = models.CharField(max_length=100, blank=True, help_text="e.g., Machine Learning, Web Development")
    certificate_id = models.CharField(max_length=100, blank=True)
    validity_period = models.CharField(max_length=50, blank=True, help_text="e.g., 2 years, Lifetime")
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    verification_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.rollno.username} - {self.title}"


# Comprehensive Audit Trail System
class AuditLog(models.Model):
    """Comprehensive audit trail for all system activities"""
    ACTION_TYPES = [
        # User actions
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('profile_update', 'Profile Updated'),
        ('password_change', 'Password Changed'),
        
        # Academic actions
        ('achievement_created', 'Achievement Created'),
        ('achievement_updated', 'Achievement Updated'),
        ('achievement_approved', 'Achievement Approved'),
        ('achievement_rejected', 'Achievement Rejected'),
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('certificate_uploaded', 'Certificate Uploaded'),
        ('certificate_verified', 'Certificate Verified'),
        
        # Administrative actions
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
        ('role_assigned', 'Role Assigned'),
        ('role_removed', 'Role Removed'),
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
        
        # Data actions
        ('data_exported', 'Data Exported'),
        ('bulk_upload', 'Bulk Data Upload'),
        ('report_generated', 'Report Generated'),
        
        # Security actions
        ('suspicious_activity', 'Suspicious Activity'),
        ('failed_login', 'Failed Login Attempt'),
        ('session_expired', 'Session Expired'),
        ('api_access', 'API Access'),
        
        # System actions
        ('backup_created', 'Backup Created'),
        ('system_maintenance', 'System Maintenance'),
        ('configuration_change', 'Configuration Changed'),
    ]
    
    # Core audit fields
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Target object (generic foreign key)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    
    # Change tracking
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Risk assessment
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ], default='low')
    
    # Additional context
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['risk_level', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action_type} by {self.user} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action_type, description, request=None, target_object=None, 
                   old_values=None, new_values=None, risk_level='low', **kwargs):
        """Convenient method to create audit log entries"""
        audit_data = {
            'user': user,
            'action_type': action_type,
            'description': description,
            'risk_level': risk_level,
        }
        
        if request:
            audit_data.update({
                'ip_address': cls.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'request_path': request.path,
                'request_method': request.method,
                'session_key': request.session.session_key,
            })
        
        if target_object:
            audit_data.update({
                'content_type': ContentType.objects.get_for_model(target_object),
                'object_id': target_object.pk,
                'object_repr': str(target_object),
            })
        
        if old_values:
            audit_data['old_values'] = old_values
        if new_values:
            audit_data['new_values'] = new_values
        
        audit_data['additional_data'] = kwargs
        
        return cls.objects.create(**audit_data)
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Enhanced Notification System
class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    TEMPLATE_TYPES = [
        ('achievement_approved', 'Achievement Approved'),
        ('achievement_rejected', 'Achievement Rejected'),
        ('achievement_submitted', 'Achievement Submitted'),
        ('project_deadline', 'Project Deadline Reminder'),
        ('certificate_verified', 'Certificate Verified'),
        ('profile_incomplete', 'Profile Incomplete'),
        ('system_maintenance', 'System Maintenance'),
        ('security_alert', 'Security Alert'),
        ('welcome', 'Welcome Message'),
        ('custom', 'Custom Template'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    
    # Email template
    email_subject = models.CharField(max_length=200, blank=True)
    email_body = models.TextField(blank=True)
    email_html_body = models.TextField(blank=True)
    
    # In-app notification template
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    
    # SMS template (if SMS integration is available)
    sms_template = models.CharField(max_length=160, blank=True)
    
    # Template variables help
    available_variables = models.TextField(blank=True, help_text="Comma-separated list of available variables")
    
    # Settings
    is_active = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render_template(self, template_text, context):
        """Render template with context variables"""
        import re
        for key, value in context.items():
            template_text = re.sub(f'{{{{{key}}}}}', str(value), template_text)
        return template_text


class EnhancedNotification(models.Model):
    """Enhanced notification system with multiple delivery channels"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('achievement', 'Achievement Related'),
        ('deadline', 'Deadline Reminder'),
        ('security', 'Security Alert'),
        ('system', 'System Notification'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low Priority'),
        ('normal', 'Normal Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ]
    
    DELIVERY_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    # Recipients
    recipient_student = models.ForeignKey(student, on_delete=models.CASCADE, null=True, blank=True)
    recipient_faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    
    # Delivery channels
    in_app_notification = models.BooleanField(default=True)
    email_notification = models.BooleanField(default=False)
    sms_notification = models.BooleanField(default=False)
    push_notification = models.BooleanField(default=False)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Scheduling
    send_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Template and context
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    context_data = models.JSONField(default=dict, blank=True)
    
    # Related object (generic foreign key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Action URL
    action_url = models.CharField(max_length=500, blank=True)
    action_text = models.CharField(max_length=50, blank=True)
    
    # Auto-delete settings
    auto_delete_after_read = models.BooleanField(default=False)
    auto_delete_days = models.IntegerField(default=30, help_text="Days after which to auto-delete")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient_student', 'is_read', 'created_at']),
            models.Index(fields=['recipient_faculty', 'is_read', 'created_at']),
            models.Index(fields=['status', 'send_at']),
        ]
    
    def __str__(self):
        recipient = self.recipient_student or self.recipient_faculty
        return f"To {recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def get_recipient(self):
        """Get the notification recipient"""
        return self.recipient_student or self.recipient_faculty
    
    @classmethod
    def create_notification(cls, recipient, title, message, notification_type='info', 
                          priority='normal', template=None, context_data=None, 
                          action_url=None, action_text=None, **kwargs):
        """Create a new notification"""
        notification_data = {
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'priority': priority,
            'template': template,
            'context_data': context_data or {},
            'action_url': action_url or '',
            'action_text': action_text or '',
        }
        
        # Set recipient based on type
        if hasattr(recipient, 'type') and recipient.type() == 'student':
            notification_data['recipient_student'] = recipient
        else:
            notification_data['recipient_faculty'] = recipient
        
        notification_data.update(kwargs)
        return cls.objects.create(**notification_data)


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    
    # Type preferences
    achievement_notifications = models.BooleanField(default=True)
    deadline_notifications = models.BooleanField(default=True)
    security_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    
    # Frequency settings
    digest_frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
        ('never', 'Never'),
    ], default='immediate')
    
    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"

    # Position or Recognition
    RECOGNITION_CHOICES = [
        ('participation', 'Participation'),
        ('appreciation', 'Appreciation'),
        ('recommendation', 'Recommendation'),
        ('completion','Completion'),
        ('recognition','Recognition'),
        ('rankcard','Rankcard'),
    ]
    rank = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    recognition = models.CharField(max_length=20, choices=RECOGNITION_CHOICES, blank=True)

    # Type of event
    EVENT_TYPE_CHOICES = [
        ('hackathon', 'Hackathon'),
        ('quiz', 'Quiz'),
        ('workshop', 'Workshop/Webinar'),
        ('techfest', 'Tech Fest'),
        ('presentation', 'Presentation'),
        ('others', 'Others'),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES,default='others')

    fest_name = models.CharField(max_length=100, blank=True)

    # Course/Domain-specific info (optional)
    course_provider = models.CharField(max_length=100, blank=True)
    domain = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=50, blank=True)

    # Technologies used (only for technical category)
    technologies = models.ManyToManyField('Technology', blank=True)

    def __str__(self):
        return f"{self.rollno} - {self.title} ({self.category})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # Only one of rank or recognition should be filled
        if self.rank and self.recognition:
            raise ValidationError("Choose either a numeric rank or a recognition type, not both.")

        if not self.rank and not self.recognition:
            raise ValidationError("You must provide either a rank or a recognition type.")

        # Technologies allowed only for 'technical' category
        if self.category != 'technical' and self.technologies.exists():
            raise ValidationError("Technologies can only be associated with Technical category.")


class Projects(models.Model):
    contributors = models.ManyToManyField(student, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField()
    YEAR_AND_SEM_CHOICES = [
        ("I-I", "I-I"), ("I-II", "I-II"), ("II-I", "II-I"), ("II-II", "II-II"),
        ("III-I", "III-I"), ("III-II", "III-II"), ("IV-I", "IV-I"), ("IV-II", "IV-II")
    ]
    year_and_sem = models.CharField(max_length=10, choices=YEAR_AND_SEM_CHOICES)
    github_link = models.URLField(blank=True, null=True)
    status_choices = [
        ("Initialized", "Initialized"),
        ("In_progress", "In Progress"),
        ("Completed", "Completed"),
    ]
    status = models.CharField(max_length=255, choices=status_choices, default="Initialized")
    technologies = models.ManyToManyField(Technology, related_name="projects", blank=True)

    def __str__(self):
        return self.title
from django.utils import timezone

class Notification(models.Model):
    recipient = models.ForeignKey("student", on_delete=models.CASCADE, related_name="notifications")
    project = models.ForeignKey("Projects", on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_accepted = models.BooleanField(null=True, blank=True)  # None = pending, True = accepted, False = declined

    def __str__(self):
        return f"{self.recipient} - {self.message[:30]}"

class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CoordinatorRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    can_view_certificates = models.BooleanField(default=False)
    can_view_publications = models.BooleanField(default=False)
    can_view_projects = models.BooleanField(default=False)
    can_view_placement = models.BooleanField(default=False)

    providers = models.ManyToManyField(Provider, blank=True)  # ⬅️ Now supports multiple providers
    faculties = models.ManyToManyField('Faculty', related_name='coordinator_roles')

    def __str__(self):
        return self.name

################## FIllOut #########################
User = get_user_model()

class FillOutForm(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="created_forms")
    assigned_students = models.ManyToManyField("student", related_name="assigned_forms")  # Assign to students
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FillOutField(models.Model):
    FIELD_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("choice", "Multiple Choice"),
        ("file_awk", "Pick from your own instances or upload file"),
    ]

    form = models.ForeignKey(FillOutForm, on_delete=models.CASCADE, related_name="fields")
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    options = models.TextField(blank=True, null=True)  # for multiple-choice
    related_model = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Model name (e.g., 'certificate', 'project')"
    )

    def __str__(self):
        return f"{self.form.title} - {self.field_name}"





class FillOutResponse(models.Model):
    form = models.ForeignKey(FillOutForm, on_delete=models.CASCADE, related_name="responses")
    student = models.ForeignKey("student", on_delete=models.CASCADE, related_name="form_responses")

    # responses structure:
    # [
    #   {
    #     "field_id": 1,
    #     "field_name": "Upload Certificate",
    #     "field_type": "file_awk",
    #     "value": {
    #         "file_url": "/media/certs/sample.pdf",
    #         OR
    #         "model": "certificate",
    #         "instance_id": 5,
    #         "display": "Python Certification"
    #     }
    #   },
    #   ...
    # ]
    responses = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.form.title}"


# PlacementOffer model: each student can have multiple offers
class PlacementOffer(models.Model):
    student = models.ForeignKey('student', on_delete=models.CASCADE, related_name='placement_offers')
    company = models.CharField(max_length=255)
    package = models.DecimalField(max_digits=8, decimal_places=2)
    offer_date = models.DateField(blank=True, null=True)
    placement_year = models.IntegerField(blank=True, null=True)
    placement_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of placement (e.g., Internship, Full-time)")
    accepted = models.BooleanField(default=False, help_text="Whether the student accepted this offer")
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        status = "Accepted" if self.accepted else "Offered"
        return f"{self.student.roll_no} - {self.company} ({status})"

# Placement model: aggregate status for student (optional, can be omitted if not needed)
class Placement(models.Model):
    student = models.OneToOneField('student', on_delete=models.CASCADE, related_name='placement_status')
    is_placed = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.roll_no} - {'Placed' if self.is_placed else 'Not Placed'}"

    def offer_count(self):
        return self.student.placement_offers.count()
