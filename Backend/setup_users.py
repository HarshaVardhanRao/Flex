#!/usr/bin/env python
"""
Quick User Setup Script for FLEX Educational Management System
Run this script to create sample users and data
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flex.settings')
django.setup()

from django.contrib.auth.models import User
from flexapp.models import student, Faculty, Role, UserRole, AchievementCategory
from datetime import datetime
from django.utils import timezone

def create_superuser():
    """Create system administrator"""
    try:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@college.edu',
            password='admin123',
            first_name='System',
            last_name='Administrator'
        )
        print("✅ Created superuser: admin (password: admin123)")
        return admin
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return None

def create_faculty():
    """Create sample faculty member"""
    try:
        # Create faculty user (Faculty extends AbstractUser)
        faculty_user = Faculty.objects.create_user(
            username='faculty001',
            email='drsmith@college.edu',
            password='faculty123',
            first_name='Dr. Jane',
            last_name='Smith',
            dept='CSE'
        )
        
        # Assign faculty role
        faculty_role = Role.objects.get(role_type='faculty')
        UserRole.objects.create(
            user=faculty_user,
            role=faculty_role,
            is_active=True
        )
        
        print("✅ Created faculty: faculty001 (password: faculty123)")
        return faculty_user
    except Exception as e:
        print(f"❌ Error creating faculty: {e}")
        return None

def create_students():
    """Create sample students"""
    students_data = [
        {
            'username': '22691A05B5',
            'roll_no': '22691A05B5',
            'first_name': 'Mahesh',
            'last_name': 'Kumar',
            'email': 'mahesh@college.edu',
            'personal_email': 'mahesh@gmail.com',
            'dept': 'CSE',
            'year': 3,
            'current_cgpa': 8.5,
            'phone': '9876543210',
            'githublink': 'https://github.com/maheshkumar',
            'linkedin_url': 'https://linkedin.com/in/maheshkumar',
            'career_interests': 'Full Stack Development, AI/ML',
            'technical_skills': 'Python, Django, React, Machine Learning, Data Science'
        },
        {
            'username': '22691A05C3',
            'roll_no': '22691A05C3',
            'first_name': 'Priya',
            'last_name': 'Sharma',
            'email': 'priya@college.edu',
            'personal_email': 'priya@gmail.com',
            'dept': 'CSE',
            'year': 2,
            'current_cgpa': 9.2,
            'phone': '9876543211',
            'githublink': 'https://github.com/priyasharma',
            'linkedin_url': 'https://linkedin.com/in/priyasharma',
            'career_interests': 'Software Development, Cybersecurity',
            'technical_skills': 'Java, Spring Boot, Angular, Cybersecurity'
        },
        {
            'username': '22691A05D7',
            'roll_no': '22691A05D7',
            'first_name': 'Arjun',
            'last_name': 'Reddy',
            'email': 'arjun@college.edu',
            'personal_email': 'arjun@gmail.com',
            'dept': 'CSE',
            'year': 4,
            'current_cgpa': 8.8,
            'phone': '9876543212',
            'githublink': 'https://github.com/arjunreddy',
            'linkedin_url': 'https://linkedin.com/in/arjunreddy',
            'career_interests': 'DevOps, Cloud Computing',
            'technical_skills': 'Docker, Kubernetes, AWS, Python, Java'
        }
    ]
    
    try:
        student_role = Role.objects.get(role_type='student')
        created_students = []
        
        for data in students_data:
            # Create student user (student extends AbstractUser)
            student_user = student.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='student123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                roll_no=data['roll_no'],
                dept=data['dept'],
                year=data['year'],
                personal_email=data['personal_email'],
                current_cgpa=data['current_cgpa'],
                phone=data['phone'],
                githublink=data['githublink'],
                linkedin_url=data['linkedin_url'],
                career_interests=data['career_interests'],
                technical_skills=data['technical_skills'],
                address=f"Student Address for {data['first_name']} {data['last_name']}, City, State - 12345"
            )
            
            # Assign role
            UserRole.objects.create(
                user=student_user,
                role=student_role,
                is_active=True
            )
            
            created_students.append(data['username'])
            
        print(f"✅ Created {len(created_students)} students: {', '.join(created_students)} (password: student123)")
        return created_students
    except Exception as e:
        print(f"❌ Error creating students: {e}")
        return []

def create_achievement_categories():
    """Create achievement categories"""
    categories = [
        {'name': 'Technical Certification', 'points': 15, 'description': 'Professional technical certifications'},
        {'name': 'Project Competition', 'points': 20, 'description': 'Participation in coding competitions and hackathons'},
        {'name': 'Research Publication', 'points': 25, 'description': 'Published research papers and articles'},
        {'name': 'Hackathon Achievement', 'points': 15, 'description': 'Awards and recognition in hackathons'},
        {'name': 'Sports Achievement', 'points': 10, 'description': 'Sports competitions and athletic achievements'},
        {'name': 'Cultural Event', 'points': 8, 'description': 'Cultural activities and artistic achievements'},
        {'name': 'Leadership Role', 'points': 12, 'description': 'Student leadership positions and responsibilities'},
        {'name': 'Community Service', 'points': 10, 'description': 'Volunteer work and community service activities'}
    ]
    
    try:
        created_categories = []
        for cat_data in categories:
            category, created = AchievementCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'points': cat_data['points'],
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_categories.append(cat_data['name'])
        
        print(f"✅ Created {len(created_categories)} achievement categories")
        return created_categories
    except Exception as e:
        print(f"❌ Error creating achievement categories: {e}")
        return []

def main():
    """Main setup function"""
    print("🚀 FLEX Educational Management System - User Setup")
    print("=" * 60)
    
    # Check if roles exist
    if Role.objects.count() == 0:
        print("❌ No roles found. Please run: python manage.py setup_roles")
        return
    
    print(f"✅ Found {Role.objects.count()} roles in system")
    
    # Create users
    print("\n👥 Creating Users...")
    admin = create_superuser()
    faculty = create_faculty()
    students = create_students()
    
    # Create categories
    print("\n🏆 Creating Achievement Categories...")
    categories = create_achievement_categories()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n🔐 Login Credentials:")
    print("Admin/Superuser:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  URL: http://localhost:8000/admin/")
    
    print("\nFaculty:")
    print("  Username: faculty001")
    print("  Password: faculty123")
    
    print("\nStudents:")
    for rollno in students:
        print(f"  Username: {rollno}")
    print("  Password: student123 (for all students)")
    
    print("\n🌐 Access URLs:")
    print("  Web Interface: http://localhost:8000/")
    print("  Admin Interface: http://localhost:8000/admin/")
    print("  API Documentation: http://localhost:8000/api/docs/")
    
    print("\n📋 Next Steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Login with any of the above credentials")
    print("3. Test the system functionality")
    print("4. Add more users via admin interface if needed")

if __name__ == "__main__":
    main()