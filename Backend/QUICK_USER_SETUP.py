"""
Simple User Creation Commands for FLEX Educational Management System
Copy and paste these commands in Django shell: python manage.py shell
"""

# ===============================================
# STEP 1: CREATE SUPERUSER (Run in terminal)
# ===============================================
# python manage.py createsuperuser
# Username: admin
# Email: admin@college.edu  
# Password: admin123

# ===============================================
# STEP 2: CREATE USERS (Run in Django shell)
# ===============================================

from django.contrib.auth.models import User
from flexapp.models import student, Faculty, Role, UserRole, AchievementCategory

# Create Faculty User
faculty = Faculty.objects.create_user(
    username='faculty001',
    email='faculty@college.edu',
    password='faculty123',
    first_name='Dr. Jane',
    last_name='Smith',
    dept='CSE'
)

# Create Students
student1 = student.objects.create_user(
    username='22691A05B5',
    email='mahesh@college.edu',
    password='student123',
    first_name='Mahesh',
    last_name='Kumar',
    roll_no='22691A05B5',
    dept='CSE',
    year=3,
    personal_email='mahesh@gmail.com',
    phone='9876543210',
    current_cgpa=8.5
)

student2 = student.objects.create_user(
    username='22691A05C3',
    email='priya@college.edu',
    password='student123',
    first_name='Priya',
    last_name='Sharma',
    roll_no='22691A05C3',
    dept='CSE',
    year=2,
    personal_email='priya@gmail.com',
    phone='9876543211',
    current_cgpa=9.2
)

# Create Achievement Categories
categories = [
    {'name': 'Technical Certification', 'points': 15},
    {'name': 'Project Competition', 'points': 20},
    {'name': 'Research Publication', 'points': 25},
    {'name': 'Hackathon Achievement', 'points': 15},
    {'name': 'Sports Achievement', 'points': 10},
    {'name': 'Cultural Event', 'points': 8}
]

for cat in categories:
    AchievementCategory.objects.get_or_create(
        name=cat['name'],
        defaults={'points': cat['points'], 'description': f'Points for {cat["name"]}'}
    )

print("✅ All users and categories created successfully!")
print("👥 Created: 1 Faculty, 2 Students, 6 Achievement Categories")

# ===============================================
# LOGIN CREDENTIALS
# ===============================================
# Admin: admin / admin123
# Faculty: faculty001 / faculty123  
# Students: 22691A05B5, 22691A05C3 / student123