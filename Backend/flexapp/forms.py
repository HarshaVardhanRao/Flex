from django import forms
from .models import LeetCode, Certificate, Projects, certifications, publications

class LeetCodeForm(forms.ModelForm):
    class Meta:
        model = LeetCode
        exclude = ['rollno']

from django import forms
from .models import Certificate

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        exclude = ['rollno', 'uploaded_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically populate distinct entries
        for field in ['source', 'course_provider', 'domain', 'fest_name']:
            self.fields[field].widget = forms.TextInput(attrs={
                'list': f'{field}_list'
            })

        # Add JS-friendly IDs for JavaScript logic
        self.fields['category'].widget.attrs.update({'id': 'id_category'})
        self.fields['technologies'].widget.attrs.update({'id': 'id_technologies'})


class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        exclude = ['technologies']

class CertificationsForm(forms.ModelForm):
    class Meta:
        model = certifications
        exclude = ['author']

class PublicationsForm(forms.ModelForm):
    class Meta:
        model = publications
        exclude = ['author']
