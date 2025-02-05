from django import forms
from .models import LeetCode, ForignLanguages, Projects

class LeetCodeForm(forms.ModelForm):
    class Meta:
        model = LeetCode
        fields = ['TotalProblems', 'easy', 'medium', 'hard']
        # Optionally, you can exclude the rollno field if you want to set it programmatically
        exclude = ['rollno']

class ForignLanguagesForm(forms.ModelForm):
    class Meta:
        model = ForignLanguages
        fields = ['source', 'title', 'certificate', 'category', 'course_link']
        # Optionally, you can exclude the rollno field if you want to set it programmatically
        exclude = ['rollno']

class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['title', 'description', 'github_link']
        # Optionally, you can exclude the rollno field if you want to set it programmatically
        exclude = ['rollno']
