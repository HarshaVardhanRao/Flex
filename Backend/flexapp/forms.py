from django import forms
from .models import LeetCode, Certificate, Projects, certifications, publications, Technology, student

class LeetCodeForm(forms.ModelForm):
    class Meta:
        model = LeetCode
        exclude = ['rollno']

from django import forms
from .models import Certificate

class CertificateForm(forms.ModelForm):
    technologies = forms.ModelMultipleChoiceField(
        queryset=Technology.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select relevant technologies (only for technical certificates)"
    )

    class Meta:
        model = Certificate
        fields = ['title', 'source', 'category', 'year_and_sem', 'certificate', 
                 'course_link', 'rank', 'recognition', 'event_type', 
                 'fest_name', 'course_provider', 'domain', 'duration', 'technologies']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Certificate Title'}),
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issuing Organization'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'category-select'}),
            'year_and_sem': forms.Select(attrs={'class': 'form-select'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'course_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Course/Certificate URL'}),
            'rank': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Rank (if applicable)'}),
            'recognition': forms.Select(attrs={'class': 'form-select'}),
            'event_type': forms.Select(attrs={'class': 'form-select', 'id': 'event-type-select'}),
            'fest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fest/Event Name (if applicable)'}),
            'course_provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Provider (if applicable)'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domain/Field of Study'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Duration (e.g., 8 weeks)'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Get the current student if available
        self.student = kwargs.pop('student', None)
        super(CertificateForm, self).__init__(*args, **kwargs)
        
        # Mark some fields as not required
        self.fields['rank'].required = False
        self.fields['recognition'].required = False
        self.fields['fest_name'].required = False
        self.fields['course_provider'].required = False
        self.fields['domain'].required = False
        self.fields['duration'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        technologies = cleaned_data.get('technologies')
        rank = cleaned_data.get('rank')
        recognition = cleaned_data.get('recognition')
        
        # Validate technologies are only for technical category
        if category != 'technical' and technologies:
            self.add_error('technologies', 'Technologies can only be selected for Technical certificates')
        
        # Validate either rank or recognition is provided, but not both
        if rank and recognition:
            self.add_error('rank', 'Please provide either rank or recognition, not both')
            self.add_error('recognition', 'Please provide either rank or recognition, not both')
        elif not rank and not recognition:
            self.add_error('rank', 'Please provide either rank or recognition')
            self.add_error('recognition', 'Please provide either rank or recognition')
            
        return cleaned_data
        
    def save(self, commit=True):
        instance = super(CertificateForm, self).save(commit=False)
        if self.student:
            instance.rollno = self.student
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
        return instance

class ProjectsForm(forms.ModelForm):
    technologies = forms.ModelMultipleChoiceField(
        queryset=Technology.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select the technologies used in this project"
    )
    
    contributors = forms.ModelMultipleChoiceField(
        queryset=student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select contributors for this project"
    )
    
    class Meta:
        model = Projects
        fields = ['title', 'description', 'year_and_sem', 'github_link', 'status', 'technologies', 'contributors']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Project Description', 'rows': 4}),
            'year_and_sem': forms.Select(attrs={'class': 'form-select'}),
            'github_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username/project'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        # Get the current student if available
        self.student = kwargs.pop('student', None)
        super(ProjectsForm, self).__init__(*args, **kwargs)
        
        # If there's a current student, preselect them
        if self.student:
            self.fields['contributors'].initial = [self.student]
        
    def clean_github_link(self):
        """Validate GitHub link format"""
        github_link = self.cleaned_data.get('github_link')
        if github_link and not (github_link.startswith('https://github.com/') or github_link.startswith('http://github.com/')):
            raise forms.ValidationError("Please enter a valid GitHub repository URL.")
        return github_link
        
    def save(self, commit=True):
        instance = super(ProjectsForm, self).save(commit=False)
        if commit:
            instance.save()
            # Make sure to save many-to-many relationships
            self.save_m2m()
            
            # Add the current student as a contributor if not already added
            if self.student and not instance.contributors.filter(id=self.student.id).exists():
                instance.contributors.add(self.student)
                
        return instance
        if github_link and not (github_link.startswith('https://github.com/') or github_link.startswith('http://github.com/')):
            raise forms.ValidationError("Please enter a valid GitHub repository URL.")
        return github_link

class CertificationsForm(forms.ModelForm):
    class Meta:
        model = certifications
        exclude = ['author']

class PublicationsForm(forms.ModelForm):
    class Meta:
        model = publications
        exclude = ['author']
