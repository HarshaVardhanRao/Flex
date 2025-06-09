from rest_framework import serializers
from .models import student, Projects, Certificate, Technology

class StudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name', read_only=True)
    class Meta:
        model = student
        fields = ['id', 'roll_no', 'dept', 'section', 'name']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = '__all__'
