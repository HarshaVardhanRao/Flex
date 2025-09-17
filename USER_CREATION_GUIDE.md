# FLEX Educational Management System - User Creation Guide

## Database Status
✅ **Database Cleared Successfully**  
✅ **Roles Recreated**: 7 roles with proper permissions  
✅ **Ready for User Creation**

## User Creation Methods

### Method 1: Django Admin Interface (Recommended)

#### Step 1: Create Superuser
```bash
python manage.py createsuperuser
```
**Follow the prompts to set:**
- Username (e.g., admin)
- Email address
- Password

#### Step 2: Access Admin Interface
1. Start the server: `python manage.py runserver`
2. Go to: http://localhost:8000/admin/
3. Login with superuser credentials

#### Step 3: Create Users via Admin
Navigate to:
- **Auth > Users** → Create Django users
- **Flexapp > Students** → Create student profiles
- **Flexapp > Faculty** → Create faculty profiles
- **Flexapp > User Roles** → Assign roles to users

### Method 2: Django Shell (Advanced Users)

#### Create Superuser via Shell
```python
# Start shell: python manage.py shell

from django.contrib.auth.models import User
from flexapp.models import student, Faculty, Role, UserRole

# Create superuser
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@college.edu',
    password='admin123',
    first_name='System',
    last_name='Administrator'
)
```

#### Create Student User
```python
# Create Django user
student_user = User.objects.create_user(
    username='22691A05B5',  # Roll number as username
    email='student@college.edu',
    password='student123',
    first_name='John',
    last_name='Doe'
)

# Create student profile
student_profile = student.objects.create(
    rollno='22691A05B5',
    name='John Doe',
    email='student@college.edu',
    personal_email='john.doe@gmail.com',
    dept='Computer Science',
    year='III',
    cgpa=8.5,
    phone='9876543210',
    github_link='https://github.com/johndoe',
    linkedin_profile='https://linkedin.com/in/johndoe',
    career_interests='Software Development, AI/ML',
    skills='Python, Django, React, Machine Learning',
    address='123 Student Street, City, State - 12345'
)

# Assign student role
student_role = Role.objects.get(role_type='student')
UserRole.objects.create(
    user=student_user,
    role=student_role,
    is_active=True
)
```

#### Create Faculty User
```python
# Create Django user
faculty_user = User.objects.create_user(
    username='faculty001',
    email='faculty@college.edu',
    password='faculty123',
    first_name='Dr. Jane',
    last_name='Smith'
)

# Create faculty profile
faculty_profile = Faculty.objects.create(
    name='Dr. Jane Smith',
    email='faculty@college.edu',
    dept='Computer Science',
    designation='Associate Professor',
    phone='9876543210',
    research_interests='Machine Learning, Data Science, Software Engineering'
)

# Assign faculty role
faculty_role = Role.objects.get(role_type='faculty')
UserRole.objects.create(
    user=faculty_user,
    role=faculty_role,
    is_active=True
)
```

### Method 3: Management Commands

#### Assign Roles to Existing Users
```bash
# Assign admin role
python manage.py assign_role admin super_admin

# Assign faculty role with department
python manage.py assign_role faculty001 faculty --department "Computer Science"

# Assign coordinator role with expiration
python manage.py assign_role coord001 coordinator --department "IT" --duration 365
```

## Quick Setup Script

### Create Sample Data
```python
# Run in Django shell: python manage.py shell

from django.contrib.auth.models import User
from flexapp.models import student, Faculty, Role, UserRole, AchievementCategory
from datetime import datetime, timedelta
from django.utils import timezone

# 1. Create Superuser
admin = User.objects.create_superuser(
    username='admin',
    email='admin@college.edu',
    password='admin123',
    first_name='System',
    last_name='Administrator'
)

# 2. Create Faculty
faculty_user = User.objects.create_user(
    username='faculty001',
    email='drsmith@college.edu',
    password='faculty123',
    first_name='Dr. Jane',
    last_name='Smith'
)

faculty_profile = Faculty.objects.create(
    name='Dr. Jane Smith',
    email='drsmith@college.edu',
    dept='Computer Science',
    designation='Associate Professor',
    phone='9876543210',
    research_interests='Machine Learning, Data Science'
)

faculty_role = Role.objects.get(role_type='faculty')
UserRole.objects.create(user=faculty_user, role=faculty_role, is_active=True)

# 3. Create Students
students_data = [
    {
        'rollno': '22691A05B5',
        'name': 'Mahesh Kumar',
        'email': 'mahesh@college.edu',
        'personal_email': 'mahesh@gmail.com',
        'dept': 'Computer Science',
        'year': 'III',
        'cgpa': 8.5
    },
    {
        'rollno': '22691A05C3',
        'name': 'Priya Sharma',
        'email': 'priya@college.edu',
        'personal_email': 'priya@gmail.com',
        'dept': 'Information Technology',
        'year': 'II',
        'cgpa': 9.2
    }
]

student_role = Role.objects.get(role_type='student')

for data in students_data:
    # Create Django user
    user = User.objects.create_user(
        username=data['rollno'],
        email=data['email'],
        password='student123',
        first_name=data['name'].split()[0],
        last_name=' '.join(data['name'].split()[1:])
    )
    
    # Create student profile
    student_profile = student.objects.create(
        rollno=data['rollno'],
        name=data['name'],
        email=data['email'],
        personal_email=data['personal_email'],
        dept=data['dept'],
        year=data['year'],
        cgpa=data['cgpa'],
        phone='9876543210',
        career_interests='Software Development',
        skills='Python, Django, JavaScript'
    )
    
    # Assign role
    UserRole.objects.create(user=user, role=student_role, is_active=True)

# 4. Create Achievement Categories
categories = [
    {'name': 'Technical Certification', 'points': 15},
    {'name': 'Project Competition', 'points': 20},
    {'name': 'Research Publication', 'points': 25},
    {'name': 'Hackathon', 'points': 15},
    {'name': 'Sports Achievement', 'points': 10},
    {'name': 'Cultural Event', 'points': 8}
]

for cat_data in categories:
    AchievementCategory.objects.create(
        name=cat_data['name'],
        points=cat_data['points'],
        description=f"Achievements in {cat_data['name'].lower()}"
    )

print("✅ Sample data created successfully!")
print("👥 Users created: Admin, 1 Faculty, 2 Students")
print("🏆 Achievement categories: 6 categories")
print("🔐 All users have proper role assignments")
```

## Login Credentials

### Default Credentials (After Setup)
```
🔧 Admin/Superuser:
   Username: admin
   Password: admin123
   
👨‍🏫 Faculty:
   Username: faculty001
   Password: faculty123
   
👨‍🎓 Students:
   Username: 22691A05B5  (Mahesh Kumar)
   Password: student123
   
   Username: 22691A05C3  (Priya Sharma)
   Password: student123
```

## Role Hierarchy

### Available Roles
1. **Super Admin** (Level 100) - Full system access
2. **Admin** (Level 90) - Administrative functions
3. **HOD** (Level 80) - Department head privileges
4. **Coordinator** (Level 70) - Program coordination
5. **Faculty** (Level 60) - Teaching and assessment
6. **Student** (Level 10) - Profile and achievements
7. **Guest** (Level 1) - Read-only access

### Role Permissions
- **Super Admin**: All permissions
- **Admin**: User management, system settings
- **Faculty**: Student assessment, achievement approval
- **Student**: Profile management, achievement submission

## Authentication Methods

### Web Login
- URL: http://localhost:8000/login
- Use roll number/username and password

### API Authentication
```bash
# JWT Token Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "22691A05B5", "password": "student123"}'

# API Key (for external integrations)
# Use the previously created API key: PBZMrc58N1v8sSmCI7UzOMh3jCEiKqMf
```

## Next Steps

### 1. Start the Server
```bash
python manage.py runserver
```

### 2. Create Users
Choose your preferred method:
- **Admin Interface**: http://localhost:8000/admin/
- **Django Shell**: Run the quick setup script above
- **Management Commands**: Use custom commands

### 3. Test the System
1. Login with different user types
2. Test role-based access
3. Create sample achievements
4. Test API endpoints

### 4. Customize Data
- Add more students via admin interface
- Create additional faculty members
- Set up department-specific coordinators
- Configure notification templates

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure proper role assignments
2. **Login Failed**: Check username (use roll number for students)
3. **Missing Roles**: Run `python manage.py setup_roles`
4. **Database Issues**: Run migrations with `python manage.py migrate`

### Reset Instructions
```bash
# If you need to start over
python manage.py flush --noinput
python manage.py setup_roles
# Then create users again
```

---
**Status**: ✅ Database cleared and ready for user creation  
**Next**: Choose your preferred user creation method and start adding users!