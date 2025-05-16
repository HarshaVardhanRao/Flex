from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model

from django.db import models

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

    def __str__(self):
        return self.first_name
    def type(self):
        return "student"


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
    github_link = models.URLField(blank=True)
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


