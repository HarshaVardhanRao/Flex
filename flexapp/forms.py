from django import forms
from .models import LeetCode, Certificate, Projects, certifications, publications

class LeetCodeForm(forms.ModelForm):
    class Meta:
        model = LeetCode
        exclude = ['rollno']

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        exclude = ['rollno', 'uploaded_at']

class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = '__all__'

class CertificationsForm(forms.ModelForm):
    class Meta:
        model = certifications
        exclude = ['author']

class PublicationsForm(forms.ModelForm):
    class Meta:
        model = publications
        exclude = ['author']
