from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model

class publications(models.Model):
    author = models.ForeignKey("Faculty", on_delete=models.CASCADE, related_name="publications")
    title = models.CharField(max_length=100)
    publication_date = models.DateField()
    publication_type = models.CharField(max_length=50)
    publication_link = models.URLField()
    publication_area = models.CharField(max_length=50)
    publication_volume = models.CharField(max_length=50)
    publication_notes = models.TextField()
    publication_status = models.CharField(max_length=50)
    publication_journal = models.CharField(max_length=100)
    publication_abstract = models.TextField()
    publication_keywords = models.TextField()
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
    github_link = models.URLField(blank=True,null=True)
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

class ForignLanguages(models.Model):
    rollno = models.ForeignKey(student,on_delete=models.CASCADE, related_name="ForeignLanguages")
    source = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    certificate = models.FileField(upload_to='certificates/',null=True)
    TECHNICAL = 'technical'
    FOREIGN_LANGUAGE = 'foreign_language'
    CATEGORY_CHOICES = [
        (TECHNICAL,'Technical'),
        (FOREIGN_LANGUAGE,'Foreign Language'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=TECHNICAL)
    YEAR_AND_SEM_CHOICES = [("I-I", "I-I"), ("I-II", "I-II"), ("II-I", "II-I"), ("II-II", "II-II"), ("III-I", "III-I"), ("III-II", "III-II"), ("IV-I", "IV-I"), ("IV-II", "IV-II")]
    year_and_sem = models.CharField(max_length=10, choices=YEAR_AND_SEM_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    course_link = models.URLField(blank=True)
    def __str__(self):
        return f"{self.rollno} - {self.title}"

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


User = get_user_model()

class FillOutForm(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_forms")
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
    ]

    form = models.ForeignKey(FillOutForm, on_delete=models.CASCADE, related_name="fields")
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    options = models.TextField(blank=True, null=True)  # JSON list for multiple choices

    def __str__(self):
        return f"{self.form.title} - {self.field_name}"


class FillOutResponse(models.Model):
    form = models.ForeignKey(FillOutForm, on_delete=models.CASCADE, related_name="responses")
    student = models.ForeignKey("student", on_delete=models.CASCADE, related_name="form_responses")
    responses = models.JSONField()  # Store responses as JSON
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.form.title}"


