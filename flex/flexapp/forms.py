from django import forms
from .models import *

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        exclude = ['rollno']
class LeetCodeForm(forms.ModelForm):
    class Meta:
        model = LeetCode
        exclude = ['rollno']

class ForignLanguageForm(forms.ModelForm):#Overall certifications including Technical and workshops
    class Meta:
        model = ForignLanguages
        exclude = ['rollno']

