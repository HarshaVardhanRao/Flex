from django.db import models
from django.contrib.auth.models import AbstractUser


class student(AbstractUser):
    roll_no = models.CharField(max_length=12)
    DEPT_CHOICES = [
        ("CSE","CSE"),("CAI","CAI"),("CSD","CSD"),("CSM","CSM"),("CSC","CSC"),("CST","CST"),("ECE","ECE"),("EEE","EEE"),("CE","CE"),("ME","ME")
    ]
    SECTION_CHOICES = [
        ("A","A"),("B","B"),("C","C"),("D","D"),("E","E"),("F","F")
    ]
    dept= models.CharField(max_length=20, choices=DEPT_CHOICES, default="CSE")
    section = models.CharField(max_length=10,choices=SECTION_CHOICES, default="A")
    def __str__(self):
        return self.first_name

class LeetCode(models.Model):
    TotalProblems = models.IntegerField(default=0)
    rollno = models.ForeignKey(student,on_delete=models.CASCADE)
    easy = models.IntegerField(default=0)
    medium = models.IntegerField(default=0)
    hard = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.rollno} - Total Problems Solved: {self.TotalProblems}"

class ForignLanguages(models.Model):
    rollno = models.ForeignKey(student,on_delete=models.CASCADE)
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
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    course_link = models.URLField(blank=True)
    def __str__(self):
        return f"{self.rollno} - {self.title}"

class Projects(models.Model):
    rollno = models.ForeignKey(student,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    github_link = models.URLField(blank=True)
    def __str__(self):
        return f"{self.rollno} - {self.title}"





