
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
import logging
from django.contrib.auth.decorators import login_required
from .models import Projects, Certificate, student, LeetCode, Faculty,FillOutForm, FillOutField, student, Technology
import requests
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import pandas as pd
from django.core.mail import send_mail
import random
from flex import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import StudentSerializer, ProjectSerializer, CertificateSerializer, TechnologySerializer
from django.db.models import F
from .forms import PlacementOfferForm

# Faculty: Add placement offer for any student
@login_required
def add_placement_offer_faculty(request):
    if request.user.type() != "Faculty":
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        form = PlacementOfferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Placement offer added successfully!")
            return redirect('faculty_dashboard')  # Change to your faculty dashboard name
    else:
        form = PlacementOfferForm()
    return render(request, 'add_placement_offer_faculty.html', {'form': form})

# Student: Add placement offer for self
@login_required
def add_placement_offer_student(request):
    if request.user.type() != "student":
        return HttpResponse("Unauthorized", status=403)
    if request.method == 'POST':
        form = PlacementOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.student = request.user
            offer.save()
            messages.success(request, "Placement offer added successfully!")
            return redirect('dashboard')
    else:
        form = PlacementOfferForm()
        form.fields['student'].widget = forms.HiddenInput()
    return render(request, 'add_placement_offer_student.html', {'form': form})
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# Export Placement Report View
@csrf_exempt
def export_placement_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('type')
        # Dummy implementation: return a simple response for now
        if report_type == 'college':
            return HttpResponse('College Summary Report (dummy)', content_type='text/plain')
        elif report_type == 'dept':
            return HttpResponse('Department Summary Report (dummy)', content_type='text/plain')
        elif report_type == 'excel':
            return HttpResponse('Excel Export (dummy)', content_type='text/plain')
        elif report_type == 'pdf':
            return HttpResponse('PDF Export (dummy)', content_type='text/plain')
        else:
            return HttpResponse('Unknown report type', content_type='text/plain')
    return HttpResponse('Invalid request', content_type='text/plain')


def index(request):
    if request.user.is_authenticated:
        print(request.user)
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        if request.user.type() == "student":
            return redirect('dashboard')
        if request.user.type() == "Faculty":
            return redirect('faculty')
    print("redirecting to Login")
    return redirect('login')

logging.basicConfig(level=logging.DEBUG)

# REST API endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def api_overview(request):
    api_urls = {
        'Student List': '/api/students/',
        'Student Detail': '/api/student/<str:rollno>/',
        'Projects': '/api/projects/',
        'Certificates': '/api/certificates/',
    }
    return Response(api_urls)

@api_view(['GET'])
@permission_classes([AllowAny])
def student_list(request):
    students = student.objects.values('id', 'roll_no', 'dept', 'section', 'first_name')
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def student_detail(request, rollno):
    student_obj = get_object_or_404(student, rollno=rollno)
    serializer = StudentSerializer(student_obj)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_login(request):
    rollno = request.data.get('username')
    password = request.data.get('password')

    if not rollno or not password:
        return Response({'error': 'Please provide both username and password'}, status=400)

    user = authenticate(request=request, username=rollno, password=password)

    if user is not None:
        login(request, user)
        try:
            if user.type() == "student":
                serializer = StudentSerializer(user)
                return Response(serializer.data)
            else:
                return Response({'error': 'Only student login supported via API'}, status=403)
        except AttributeError:
            return Response({'error': 'User type not supported'}, status=500)
    else:
        # Log the failed attempt for debugging
        logging.debug(f"Failed login attempt for username: {rollno}")
        return Response({'error': 'Invalid credentials. Please check your username and password.'}, status=401)

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow any access to check auth status
def api_current_user(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=401)

    try:
        user_type = request.user.type()
        if user_type == "student":
            serializer = StudentSerializer(request.user)
            return Response(serializer.data)
        else:
            return Response({'error': 'Currently only student accounts are supported'}, status=403)
    except AttributeError:
        return Response({'error': 'User type not supported'}, status=403)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any user to logout
@csrf_exempt
def api_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return Response({"message": "Successfully logged out"})

@api_view(['GET'])
@permission_classes([AllowAny])
def technology_list(request):
    technologies = Technology.objects.all()
    serializer = TechnologySerializer(technologies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def project_list(request):
    projects = Projects.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_api(request):
    """API endpoint for creating a new project"""
    try:
        # Get current user
        current_user = request.user

        # Check if the user is a student
        if not hasattr(current_user, 'type') or current_user.type() != "student":
            return Response({"error": "Only students can create projects"}, status=403)

        # Create a form with the request data
        form = ProjectsForm(request.data, student=current_user)

        if form.is_valid():
            project = form.save(commit=False)
            project.save()

            # Save many-to-many relationships
            form.save_m2m()

            # Add current user as contributor if not already added
            if current_user not in project.contributors.all():
                project.contributors.add(current_user)

            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=201)
        else:
            return Response({"errors": form.errors}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def certificate_list(request):
    certificates = Certificate.objects.all()
    serializer = CertificateSerializer(certificates, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_certificate_api(request):
    """API endpoint for creating a new certificate"""
    try:
        # Get current user
        current_user = request.user

        # Check if the user is a student
        if not hasattr(current_user, 'type') or current_user.type() != "student":
            return Response({"error": "Only students can add certificates"}, status=403)

        # Handle file upload if present
        certificate_file = request.FILES.get('certificate')

        # Create a copy of the data that can be modified
        data = request.data.copy()

        # Create a form with the request data
        form = CertificateForm(data, request.FILES, student=current_user)

        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.rollno = current_user
            certificate.save()

            # Save many-to-many relationships
            form.save_m2m()

            serializer = CertificateSerializer(certificate)
            return Response(serializer.data, status=201)
        else:
            return Response({"errors": form.errors}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

def getStudentDetails(student):
    try:
        # Ensure we are querying the correct model field
        projects = Projects.objects.filter(contributors=student)  # Updated line
        # projects = student.projects.all()
        print(projects)

        Tech_certifications = Certificate.objects.filter(rollno=student, category="Technical")
        For_lang = Certificate.objects.filter(rollno=student, category="Foreign Language")

        return {
            "name": student.first_name,
            "rollno": student.roll_no,
            "dept": student.dept,
            "section": student.section,
            "leetcode_user": student.leetcode_user,
            'projects': serializers.serialize('json', projects),
            'Technical': serializers.serialize('json', Tech_certifications),
            'Foreign_languages': serializers.serialize('json', For_lang)
        }
    except Exception as e:
        logging.error(f"Error in getStudentDetails: {e}")
        return {}


@login_required
def dashboard(request):
    try:
        context = getStudentDetails(request.user)
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logging.error(f"Error in dashboard: {e}")
        return HttpResponse("An error occurred.")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import logging
from .models import Projects, Technology, student

@login_required
def search_students(request):
    if "term" in request.GET:
        query = request.GET.get("term", "")
        print(query)
        students = student.objects.filter(first_name__icontains=query)[:10]  # Limit results
        students_list = [{"id": s.id, "text": s.first_name} for s in students]
        return JsonResponse(students_list, safe=False)
    return JsonResponse([], safe=False)

def search_technologies(request):
    term = request.GET.get("term", "")
    technologies = Technology.objects.filter(name__icontains=term).values("id", "name")
    return JsonResponse(list(technologies), safe=False)

@csrf_exempt
def create_technology(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            
            if not name:
                return JsonResponse({'error': 'Technology name is required'}, status=400)
            
            # Check if technology already exists (case-insensitive)
            existing_tech = Technology.objects.filter(name__iexact=name).first()
            if existing_tech:
                return JsonResponse({
                    'id': existing_tech.id,
                    'name': existing_tech.name,
                    'message': 'Technology already exists'
                })
            
            # Create new technology
            new_tech = Technology.objects.create(name=name.capitalize())
            return JsonResponse({
                'id': new_tech.id,
                'name': new_tech.name,
                'message': 'Technology created successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

def clean_list(lst_str):
    return list(map(int, ast.literal_eval(lst_str)[0].split(',')))

import ast
import logging
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Projects, student, Technology

def extract_languages_from_github(github_url, project_instance):
    try:
        if "github.com/" not in github_url:
            return

        parts = github_url.strip('/').split("github.com/")[-1].split('/')
        if len(parts) < 2:
            return

        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        response = requests.get(api_url)
        if response.status_code != 200:
            return

        data = response.json()
        languages = list(data.keys())
        print(languages)

        for lang in languages:
            tech_obj, _ = Technology.objects.get_or_create(name=lang.capitalize())
            project_instance.technologies.add(tech_obj)

    except Exception as e:
        print(f"Error extracting languages: {e}")


@login_required
def create_project(request):
    try:
        if request.method == 'POST':
            title = request.POST.get('project-name')
            description = request.POST.get('description')
            year_and_sem = request.POST.get('year-and-sem')
            status = request.POST.get('status', 'Initialized')
            github_link = request.POST.get('github')
            contributors_ids = request.POST.getlist('contributors')
            print(type(contributors_ids))
            tech_names = request.POST.getlist('technologies')

            from itertools import chain
            contributors_ids = list(
                chain.from_iterable(id_str.split(',') for id_str in contributors_ids)
            )
            contributors_ids = [int(id.strip()) for id in contributors_ids if id.strip().isdigit()]
            print(contributors_ids)

            tech_names = [tech.strip().capitalize() for tech in tech_names if tech.strip()]

            # Step 1: Create project first
            new_project = Projects.objects.create(
                title=title,
                description=description,
                year_and_sem=year_and_sem,
                github_link=github_link,
                status=status
            )

            # Step 2: Add current user if student
            if request.user.type() == "student":
                new_project.contributors.add(request.user.id)

            # Step 3: Add additional contributors
            contributors = student.objects.filter(id__in=contributors_ids)
            new_project.contributors.add(*contributors)

            # Step 4: Add selected technologies
            tech_objects = []
            for tech_name in tech_names:
                tech_obj, _ = Technology.objects.get_or_create(name=tech_name)
                tech_objects.append(tech_obj)
            new_project.technologies.add(*tech_objects)

            # Step 5: Extract GitHub languages if none selected
            if not tech_objects and github_link:
                extract_languages_from_github(github_link, new_project)

            new_project.save()
            print(new_project," saved")
            return redirect('dashboard')

        # GET request
        students = student.objects.all()
        technologies = Technology.objects.all()
        return render(request, 'dashboard.html', {'students': students, 'technologies': technologies})

    except Exception as e:
        logging.error(f"Error in create_project: {e}")
        return HttpResponse("An error occurred.")

@login_required
def add_certification(request):
    try:
        if request.method == 'POST':
            rollno = request.user
            course_type = request.POST.get('type')
            title = request.POST.get('course-name')
            source = request.POST.get('provider')
            status = request.POST.get('status')
            course_link = request.POST.get('course-link')
            new_course = Certificate(rollno=rollno, title=title, source=source, course_link=course_link, category=course_type)
            new_course.save()
            return redirect('dashboard')
        return render(request, 'dashboard.html')
    except Exception as e:
        logging.error(f"Error in add_certification: {e}")
        return HttpResponse("An error occurred.")

def CustomLogin(request):
    print("LoginBlock")
    try:
        if request.user.is_authenticated:
            print(request.user)
            if request.user.is_superuser:
                return redirect('admin')
            if request.user.type() == "student":
                return redirect('dashboard')
            if request.user.type() == "Faculty":
                return redirect('faculty')


        if request.method == 'POST':
            rollno = request.POST.get('rollno')
            password = request.POST.get('password')
            print(rollno,password)
            user = authenticate(request=request, username=rollno, password=password)
            print(user)
            if user is not None:
                login(request, user)
                if user.type() == "student":
                    return redirect('dashboard')
                if user.type() == "Faculty":
                    return redirect('faculty')
        return render(request, 'login.html')
    except Exception as e:
        logging.error(f"Error in CustomLogin: {e}")
        return HttpResponse("An error occurred.")

@login_required
def CustomLogout(request):
    try:
        logout(request)
        return redirect('/')
    except Exception as e:
        logging.error(f"Error in CustomLogout: {e}")
        return HttpResponse("An error occurred.")

################################FillOut##########################
@login_required
def fillout(request):
    if request.user.is_superuser or request.user.type() == "Faculty":
        return redirect('forms/')
    else:
        return redirect('assigned/')

def create_form(request):
    if request.user.type() != "Faculty":
        return JsonResponse({"error": "Unauthorized"}, status=403)

    if request.method == "POST":
        try:
            title = request.POST.get("title")
            description = request.POST.get("description", "")
            assigned_ids = request.POST.get("assigned_students", "").split(",")

            form = FillOutForm.objects.create(
                title=title,
                description=description,
                created_by=request.user,
            )

            # Process fields
            fields = []
            for key in request.POST:
                if "field_name" in key:
                    idx = key.split("[")[1].split("]")[0]
                    field_name = request.POST.get(f"fields[{idx}][field_name]")
                    field_type = request.POST.get(f"fields[{idx}][field_type]")
                    options = request.POST.get(f"fields[{idx}][options]", None)
                    related_model = request.POST.get(f"fields[{idx}][related_model]", None)

                    fields.append(FillOutField(
                        form=form,
                        field_name=field_name,
                        field_type=field_type,
                        options=json.dumps([o.strip() for o in options.split(",")]) if options else None,
                        related_model=related_model if field_type == "file_awk" else None
                    ))

            FillOutField.objects.bulk_create(fields)
            form.assigned_students.set(student.objects.filter(id__in=assigned_ids))
            return JsonResponse({"message": "Form created", "form_id": form.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    print("Html Requested")
    all_students = student.objects.select_related("mentor").all()
    years = student.objects.values_list("year", flat=True).distinct()
    sections = student.objects.values_list("section", flat=True).distinct()

    return render(request, "create_form.html", {
        "students": all_students,
        "years": years,
        "sections": sections,
    })


def student_model_instances(request, model_name):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    model_map = {
        "certificate": Certificate,
        "project": Project,
    }

    model = model_map.get(model_name)
    if not model:
        return JsonResponse({"error": "Invalid model"}, status=400)

    instances = model.objects.filter(student=request.user)
    data = [{"id": obj.id, "label": str(obj)} for obj in instances]
    return JsonResponse(data, safe=False)


@csrf_exempt
def submit_response(request, form_id):
    if request.method == "POST":
        data = json.loads(request.body)
        form = get_object_or_404(FillOutForm, id=form_id)
        student_obj = request.user  # Assuming logged-in student
        FillOutResponse.objects.create(form=form, student=student_obj, responses=data["responses"])
        return JsonResponse({"message": "Response submitted successfully!"})
################################## Otp ##################################################
import smtplib
from email.mime.text import MIMEText
def send_otp(email):
    try:
        otp = random.randint(100000, 999999)
        logging.debug(f"Generated OTP: {otp}")
        sender_email = "webclubmits@gmail.com"
        sender_password = "zpco iaxk aywo rcwg"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        recipient_email = email

        # Create message
        subject = "OTP for Verification"
        body = f"Your OTP for login into the Internship Dashboard is: {otp}"
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email

    # Connect to the server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            # Log in to the email account
            server.login(sender_email, sender_password)
            # Send the email
            server.sendmail(sender_email, recipient_email, message.as_string())
            print("OTP sent successfully.")
        return otp
    except Exception as e:
        logging.error(f"Error in send_otp: {e}")
        return None


def verify_otp(request):
    try:
        if request.method == 'POST':
            otp = request.POST.get('otp')
            print(otp)
            print(str(request.session['otp']))
            if otp == str(request.session['otp']):
                user = student.objects.create_user(
                    username=request.session.get('rollno'),
                    roll_no=request.session.get('rollno'),
                    is_staff=request.session.get('is_staff'),
                    first_name=request.session.get('first_name'),
                    dept=request.session.get('deptt'),
                    section=request.session.get('section'),
                    year=request.session.get('year'),
                    leetcode_user=request.session.get('leetcode_user'),
                )
                user.set_password(request.session.get('password'))
                user.save()
                print(f"{user.username}: {user.password}")
                leetcode = LeetCode.objects.create(rollno=user)
                leetcode.save()
                authenticated_user = authenticate(username=user.username, password=request.session.get('password'))
                if authenticated_user is not None:
                    login(request, authenticated_user, backend='flexapp.auth_backends.StudentBackend')
                    logging.debug(f"User logged in: {authenticated_user}")
                    return redirect('dashboard')
                else:
                    logging.error("Authentication failed.")
                    return redirect('login')
            else:
                logging.error('Invalid OTP')
                return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})

        return render(request, 'verify_otp.html')
    except Exception as e:
        logging.error(f"Error in verify_otp: {e}")
        return HttpResponse("An error occurred.")
def register(request):
    try:
        if request.method == 'POST':
            request.session['rollno'] = request.POST.get('rollno')
            request.session['password'] = request.POST.get('password')
            request.session['first_name'] = request.POST.get('first_name')
            request.session['role'] = request.POST.get('role')
            request.session['deptt'] = request.POST.get('dept')
            request.session['section'] = request.POST.get('section')
            request.session['year'] = request.POST.get('year')
            request.session['is_staff'] = request.POST.get('role') == 'staff'
            request.session['leetcode_user'] = request.POST.get('leetcode_user')

            stu_email = f"{request.session['rollno']}@mits.ac.in"

            try:
                otp = send_otp(stu_email)
                request.session['otp'] = otp
                logging.debug(f"OTP sent: {otp}")

                return redirect('verify_otp')

            except Exception as e:
                logging.error(f"Error during registration: {e}")
                return render(request, 'register.html', {'error': str(e)})

        return render(request, 'register.html')
    except Exception as e:
        logging.error(f"Error in register: {e}")
        return HttpResponse("An error occurred.")
from django.db.models import Count, Avg
@login_required
def faculty(request):
    try:
        from .models import student, Certificate, Technology, Projects, Faculty  # or whatever your model is called

        # Get unique values for filter options
        certificate_providers = list(Certificate.objects.exclude(source='').values_list('source', flat=True).distinct().order_by('source'))
        course_providers = list(Certificate.objects.exclude(course_provider='').values_list('course_provider', flat=True).distinct().order_by('course_provider'))
        
        # Combine both source and course_provider into one list for the filter
        all_providers = sorted(list(set(certificate_providers + course_providers)))
        
        # Get all technologies
        technologies = list(Technology.objects.all().values_list('name', flat=True).distinct().order_by('name'))
        
        # Get unique domains from certificates
        domains = list(Certificate.objects.exclude(domain='').values_list('domain', flat=True).distinct().order_by('domain'))
        
        # Get certificate categories
        certificate_categories = [choice[0] for choice in Certificate.CATEGORY_CHOICES]
        
        # Get project statuses
        project_statuses = [choice[0] for choice in Projects.status_choices]
        
        # Get faculty list for mentor filter
        mentors = list(Faculty.objects.all().values_list('first_name', flat=True).distinct().order_by('first_name'))
        
        # Get department choices
        departments = [choice[0] for choice in student.DEPT_CHOICES]

        studentData = list(
            student.objects.filter(is_superuser=False)
            .annotate(
                project_count=Count('projects', distinct=True),
                certificate_count=Count('certificates', distinct=True)
            )
            .values(
                'roll_no', 'first_name', 'dept', 'year', 'section',
                'studentrollno__TotalProblems',  # double-check this name
                'project_count', 'certificate_count', 'mentor__first_name'
            )
        )
        
        # Add additional information to each student
        for student_data in studentData:
            student_obj = student.objects.get(roll_no=student_data['roll_no'])
            
            # Certificate provider information
            student_certificates = Certificate.objects.filter(rollno=student_obj)
            student_providers = []
            student_domains = []
            student_cert_categories = []
            
            for cert in student_certificates:
                if cert.source:
                    student_providers.append(cert.source)
                if cert.course_provider:
                    student_providers.append(cert.course_provider)
                if cert.domain:
                    student_domains.append(cert.domain)
                student_cert_categories.append(cert.category)
            
            student_data['certificate_providers'] = list(set(student_providers))
            student_data['domains'] = list(set(student_domains))
            student_data['certificate_categories'] = list(set(student_cert_categories))
            
            # Technology information from projects and certificates
            student_technologies = []
            
            # Get technologies from projects
            student_projects = Projects.objects.filter(contributors=student_obj)
            for project in student_projects:
                project_techs = project.technologies.all().values_list('name', flat=True)
                student_technologies.extend(project_techs)
            
            # Get technologies from certificates
            for cert in student_certificates:
                cert_techs = cert.technologies.all().values_list('name', flat=True)
                student_technologies.extend(cert_techs)
            
            student_data['technologies'] = list(set(student_technologies))
            
            # Project status information
            student_project_statuses = list(student_projects.values_list('status', flat=True))
            student_data['project_statuses'] = list(set(student_project_statuses))
            
        
        return render(request, 'faculty_dashboard.html', {
            'studentData': studentData,
            'certificate_providers': all_providers,
            'technologies': technologies,
            'domains': domains,
            'certificate_categories': certificate_categories,
            'project_statuses': project_statuses,
            'mentors': mentors,
            'departments': departments
        })

    except Exception as e:
        logging.error(f"Error in faculty: {e}")
        return HttpResponse("An error occurred.")
############################### DEMO #############################
from django.shortcuts import render, redirect
from .forms import CertificateForm
from .models import Certificate

def certificate_create(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.rollno = request.user  # Assuming OneToOne link
            cert.save()
            form.save_m2m()
            return redirect('/')
    else:
        form = CertificateForm()

    context = {
        'form': form,
        'distinct_sources': Certificate.objects.values_list('source', flat=True).distinct(),
        'distinct_providers': Certificate.objects.values_list('course_provider', flat=True).distinct(),
        'distinct_domains': Certificate.objects.values_list('domain', flat=True).distinct(),
        'distinct_fests': Certificate.objects.values_list('fest_name', flat=True).distinct(),
    }

    return render(request, 'certificate_form.html', context)


################################ Coordinator #####################################
# views.py
from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required

@login_required
def coordinator_dashboard(request):
    faculty = request.user  # assumes user is Faculty instance
    roles = faculty.coordinator_roles.all()

    # For layout rendering
    all_certificates = []
    all_projects = []
    all_publications = []

    for role in roles:
        if role.can_view_certificates:
            certs = Certificate.objects.all()
            if role.providers.exists():
                certs = certs.filter(provider__in=role.providers.values_list('name', flat=True))
            all_certificates.extend(list(certs))

        if role.can_view_projects:
            all_projects.extend(Projects.objects.all())

        if role.can_view_publications:
            all_publications.extend(publications.objects.all())

    context = {
        'roles': roles,
        'certificates': all_certificates,
        'projects': all_projects,
        'publications': all_publications
    }

    return render(request, 'dashboard/coordinator_dashboard.html', context)

################################ FLEX #####################################
@csrf_exempt  # Exempt from CSRF for cross-origin requests
def edit_project(request):
    try:
        if request.method == 'POST':
            # Check if we have JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                primary_key = data.get('id')
                title = data.get('name')
                description = data.get('description')
                status = data.get('status')
                github_link = data.get('github_link')
                year_and_sem = data.get('year_and_sem')
                technologies = data.get('technologies')
                new_technologies = data.get('new_technologies', [])
                contributors = data.get('contributors', [])
            else:
                # Handle form data
                primary_key = request.POST.get('id')
                title = request.POST.get('name')
                description = request.POST.get('description')
                status = request.POST.get('status')
                github_link = request.POST.get('github_link')
                year_and_sem = request.POST.get('year_and_sem')
                technologies = request.POST.getlist('technologies')
                new_technologies = request.POST.getlist('new_technologies')
                contributors = request.POST.getlist('contributors')

            print(f"Editing project with ID: {primary_key}, Title: {title}, Description: {description}, Status: {status}, GitHub Link: {github_link}")

            project = Projects.objects.get(id=primary_key)
            project.title = title
            project.description = description
            project.status = status
            project.year_and_sem = year_and_sem
            project.github_link = github_link
            project.save()
            print(f"{technologies} saved")
            # Handle technologies if present
            if technologies:
                print(f"Selected technologies: {technologies}")
                for tech_id in technologies:
                    try:
                        tech = Technology.objects.get(id=tech_id)
                        project.technologies.add(tech)
                    except Technology.DoesNotExist:
                        pass
            if new_technologies != []:
                print(f"New technologies: {new_technologies}")
                for tech_name in new_technologies:
                    tech_name = tech_name.strip().capitalize()
                    if tech_name:
                        tech, created = Technology.objects.get_or_create(name=tech_name)
                        project.technologies.add(tech)

            print(f"Contributors: {contributors}")
            if contributors:
                project.contributors.clear()
                for contributor_id in contributors:
                    try:
                        contributor = student.objects.get(id=contributor_id)
                        project.contributors.add(contributor)
                    except student.DoesNotExist:
                        pass

            # Check the Accept header to decide the response format
            if 'application/json' in request.headers.get('Accept', ''):
                # Return JSON response for API requests
                return JsonResponse({'status': 'success', 'message': 'Project updated successfully'})
            else:
                # Return redirect for browser requests
                return redirect('dashboard')
    except Exception as e:
        logging.error(f"Error in edit_project: {e}")
        if 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return HttpResponse(f"An error occurred: {e}")

def edit_certification(request):
    try:
        if request.method == 'POST':
            primary_key = request.POST.get('id')
            source = request.POST.get('provider')
            title = request.POST.get('course-name')
            course_link = request.POST.get('course-link')
            project = Certificate.objects.get(id=primary_key)
            project.source = source
            project.title = title
            project.course_link = course_link
            project.save()
            return redirect('dashboard')
    except Exception as e:
        logging.error(f"Error in edit_certification: {e}")
        return HttpResponse("An error occurred.")

def delete_project(request, primary_key):
    try:
        project = Projects.objects.get(id=primary_key)
        project.delete()
        return JSONResponse({'status': 'success', 'message': 'Project deleted successfully', 'status_code': 200})
    except Exception as e:
        logging.error(f"Error in delete_project: {e}")
        return HttpResponse("An error occurred.")

def delete_certification(request, primary_key):
    try:
        project = Certificate.objects.get(id=primary_key)
        project.delete()
        return JSONResponse({'status': 'success', 'message': 'Certification deleted successfully', 'status_code': 200})
    except Exception as e:
        logging.error(f"Error in delete_certification: {e}")
        return HttpResponse("An error occurred.")

def leetcode_request(request, leetcode_user):
    try:
        username = leetcode_user
        query = '''
        {
            matchedUser(username: "%s") {
                username
                submitStats: submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
            }
        }
        ''' % username

        url = 'https://leetcode.com/graphql'
        response = requests.post(url, json={'query': query})

        if response.status_code == 200:
            data = response.json()
            submission_data = data['data']['matchedUser']['submitStats']['acSubmissionNum']

            easy_count = next((item['count'] for item in submission_data if item['difficulty'] == 'Easy'), 0)
            medium_count = next((item['count'] for item in submission_data if item['difficulty'] == 'Medium'), 0)
            hard_count = next((item['count'] for item in submission_data if item['difficulty'] == 'Hard'), 0)
        else:
            easy_count = medium_count = hard_count = 0
        leetcode_user, created = LeetCode.objects.get_or_create(rollno=student.objects.get(leetcode_user=username))
        leetcode_user.easy = easy_count
        leetcode_user.medium = medium_count
        leetcode_user.hard = hard_count
        leetcode_user.TotalProblems = int(easy_count) + int(medium_count) + int(hard_count)
        leetcode_user.save()
        return JsonResponse({
            'easy_count': easy_count,
            'medium_count': medium_count,
            'hard_count': hard_count,
        })
    except Exception as e:
        logging.error(f"Error in leetcode_request: {e}")
        return JsonResponse({'error': 'An error occurred.'}, status=500)

################################ Download #####################################

def download_request(request):
    try:
        list = request.body
        list = json.loads(list)
        students = student.objects.filter(roll_no__in=list)
        data = []
        for stu in students:
            leetcode = LeetCode.objects.get(rollno=stu)
            technical = Certificate.objects.filter(rollno=stu, category="Technical")
            foreign = Certificate.objects.filter(rollno=stu, category="Foreign Language")
            projects = Projects.objects.filter(rollno=stu)
            data.append({
                'Roll No': stu.roll_no,
                'Student Name': stu.first_name,
                'Department': stu.dept,
                'Section': stu.section,
                'Year': stu.year,
                'Total Count': leetcode.TotalProblems,
                'Projects': ",".join([project.title for project in projects]),
                'Foreign Languages': ",".join([project.title for project in foreign]),
                'Technical Certificates': ",".join([project.title for project in technical]),
            })

        df = pd.DataFrame(data)

        # Create a response object and specify the content type for Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=students.xlsx'

        # Write the DataFrame to the response object as an Excel file
        df.to_excel(response, index=False)

        return response
    except Exception as e:
        logging.error(f"Error in download_request: {e}")
        return HttpResponse("An error occurred.")

def studentView(request, rollno):
    try:
        if request.user.type() == "Faculty":
            context = getStudentDetails(student.objects.get(roll_no=rollno))
            return render(request, 'dashboard.html', context=context)
        return HttpResponse("<h1>You are not authorized to view this page. Redirecting...</h1>\n<script>setTimeout( () => {window.location.href='/';}, 2000)</script>")
    except Exception as e:
        logging.error(f"Error in studentView: {e}")
        return HttpResponse("An error occurred.")

def forgot_password(request):
    try:
        if request.method == 'POST':
            rollno = request.POST.get('rollno')
            user = student.objects.get(roll_no=rollno)
            otp = send_otp(f"{user.roll_no}@mits.ac.in")
            print(otp)
            request.session['rollno'] = rollno
            request.session['otp'] = otp
            print(request.session['otp'])
            return redirect('verify_otp_forgot')
        else:
            return render(request, 'forgot_password.html')
    except Exception as e:
        logging.error(f"Error in forgot_password: {e}")
        return HttpResponse("An error occurred.")

def verify_otp_forgot(request):
    try:
        if request.method == 'POST':
            otp = request.POST.get('otp')
            print(otp)
            print(str(request.session['otp']))
            if otp == str(request.session['otp']):
                print("OTP Verified")
                return redirect('reset_password')
            else:
                return render(request, 'verify_otp.html', {'error': 'Invalid OTP'})
        return render(request, 'verify_otp.html')
    except Exception as e:
        logging.error(f"Error in verify_otp_forgot: {e}")
        return HttpResponse("An error occurred.")

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('confirm_password')
        user = student.objects.get(roll_no=request.session['rollno'])
        print(user)
        print(password)
        user.set_password(password)
        user.save()
        return redirect('login')
    return render(request, 'reset_password.html')



@login_required
def student_profile(request):
    user = request.user  # Get the currently logged-in user

    if request.method == "POST":
        # Only update fields provided in the POST request
        updated_fields = {}

        if 'name' in request.POST:
            name = request.POST.get("name")
            if name and name != user.first_name:
                user.first_name = name
                updated_fields['name'] = name

        if 'username' in request.POST:
            username = request.POST.get("username")
            if username and username != user.username:
                user.username = username
                updated_fields['username'] = username

        if 'leetcode_user' in request.POST:
            leetcode_user = request.POST.get("leetcode_user")
            if leetcode_user and leetcode_user != user.leetcode_user:
                user.leetcode_user = leetcode_user
                updated_fields['leetcode_user'] = leetcode_user

        if 'year' in request.POST:
            year = request.POST.get("year")
            if year and str(year) != str(user.year):
                user.year = year
                updated_fields['year'] = year

        if 'section' in request.POST:
            section = request.POST.get("section")
            if section and section != user.section:
                user.section = section
                updated_fields['section'] = section

        if updated_fields:
            try:
                user.save()
                messages.success(request, "Profile updated successfully.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.info(request, "No changes were made.")

        return redirect('profile')
    return render(request, 'student_profile_edit.html', {'user': user})


def change_ac(request,yearr):
    if request.user.is_authenticated and request.user.type() == "Faculty":
        studs = student.objects.all()
        for stu in studs:
            stu.year += yearr
            stu.save()
        return redirect('faculty')

@csrf_exempt
def upload_students(request):
    if request.method == 'POST' and request.FILES['file']:
        try:
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)

            # Read the Excel file
            df = pd.read_excel(file_path)

            # Iterate through the rows and add details to the student model
            for index, row in df.iterrows():
                s = student(
                    roll_no=row['Roll'],
                    first_name=row['Name'],
                    year=row['Year'],
                    section=row['Section'],
                    username=row['Roll']
                )
                s.set_password(row['Roll'])
                s.save()

            messages.success(request, "Students added successfully.")
            return redirect('dashboard')
        except Exception as e:
            logging.error(f"Error in upload_students: {e}")
            return HttpResponse("An error occurred.")
    return render(request, 'upload_students.html')



######################################################################################
def placement_dashboard(request):
    year = request.GET.get('year')
    tech = request.GET.get('tech')
    cert_cat = request.GET.get('cert_cat')
    domain = request.GET.get('domain')

    students = student.objects.all()
    leetcode_data = LeetCode.objects.all()
    cert_data = Certificate.objects.all()
    proj_data = Projects.objects.all()

    # if year:
    #     students = students.filter(year_and_sem__icontains=year)
    #     leetcode_data = leetcode_data.filter(rollno__year_and_sem__icontains=year)
    #     cert_data = cert_data.filter(rollno__year_and_sem__icontains=year)
    #     proj_data = proj_data.filter(year_and_sem__icontains=year)

    if tech:
        proj_data = proj_data.filter(technologies__name__icontains=tech)

    if cert_cat:
        cert_data = cert_data.filter(category=cert_cat)

    if domain:
        proj_data = proj_data.filter(domain__icontains=domain)

    context = {
        'leetcode_data': list(leetcode_data.values('rollno__dept').annotate(avg_total=Avg('TotalProblems'))),
        'cert_data': list(cert_data.values('rollno__dept', 'category').annotate(count=Count('id'))),
        'proj_data': list(proj_data.values('year_and_sem').annotate(total=Count('id'))),
        'filters': {
            'selected_year': year,
            'selected_tech': tech,
            'selected_cert_cat': cert_cat,
            'selected_domain': domain,
        }
    }
    return render(request, 'dashboard/placement_dashboard.html', context)

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import FillOutForm, FillOutField, student
from django.contrib.auth.decorators import login_required
import json


@login_required
def list_assigned_forms(request):
    assigned_forms = request.user.assigned_forms.all()
    return render(request, "fill_form_list.html", {"assigned_forms": assigned_forms})

from .models import FillOutResponse
@login_required
def fill_form(request, form_id):
    form = FillOutForm.objects.get(id=form_id)
    student = request.user

    certificates = Certificate.objects.filter(rollno=student)

    if request.method == "POST":
        responses = {}
        for field in form.fields.all():
            responses[field.field_name] = request.POST.get(str(field.id))
        FillOutResponse.objects.create(form=form, rollno=student, responses=responses)
        return redirect("assigned/")  # or wherever you want

    return render(request, "fill_form.html", {
        "form": form,
        "certificates": certificates
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import FillOutForm, FillOutField, Certificate

def get_form(request, form_id):
    form = get_object_or_404(FillOutForm, id=form_id)
    print(form)
    student = request.user
    certificates = Certificate.objects.filter(rollno=student)
    print(certificates)

    if request.method == "POST":
        responses = {}
        for field in form.fields.all():
            responses[field.field_name] = request.POST.get(str(field.id))
        form_response = FillOutResponse.objects.create(
            form=form,
            student=student,
            responses=responses
        )
        return redirect("dashboard")

    return render(request, "fill_form_detail.html", {
        "form": form,
        "fields": form.fields.all(),
        "model_instances": {
        "certificate": Certificate.objects.filter(rollno=request.user),
        "project": Projects.objects.filter(contributors=request.user),}
        })

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import FillOutForm, FillOutResponse, student
import csv

def form_list_view(request):
    faculty = request.user
    forms = FillOutForm.objects.filter(created_by=faculty)
    return render(request, 'dashboard/form_list.html', {'forms': forms})


from django.apps import apps
from django.shortcuts import render, get_object_or_404
from .models import FillOutForm, FillOutResponse

def form_detail_view(request, form_id):
    form = get_object_or_404(FillOutForm, id=form_id)
    responses = FillOutResponse.objects.filter(form=form).select_related("student")

    model_instance_map = {}

    for response in responses:
        for field in form.fields.filter(field_type="file_awk"):
            field_name = field.field_name
            model_name = field_name  # Assuming model is named same as field

            id_value = response.responses.get(field_name)
            if id_value:
                try:
                    model = apps.get_model("flexapp", model_name)
                    instance = model.objects.get(id=id_value)
                    model_instance_map[(response.id, field_name)] = instance
                except Exception:
                    model_instance_map[(response.id, field_name)] = None

    context = {
        "form": form,
        "responses": responses,
        "model_instance_map": model_instance_map,
    }
    return render(request, "dashboard/form_detail.html", context)


def download_csv(request, form_id, download_type):
    form = get_object_or_404(FillOutForm, id=form_id)
    response = HttpResponse(content_type='text/csv')

    if download_type == "responses":
        filename = f"{form.title}_responses.csv"
        writer = csv.writer(response)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer.writerow(["Student Roll No", "Student Name", "Submitted At"] + [f.field_name for f in form.fields.all()])
        for r in FillOutResponse.objects.filter(form=form):
            student_info = [r.student.roll_no, r.student.first_name, r.submitted_at]
            answers = [r.responses.get(f.field_name, "") for f in form.fields.all()]
            writer.writerow(student_info + answers)

    elif download_type == "filled":
        filename = f"{form.title}_filled.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow(["Roll No", "Name"])
        for student_obj in form.assigned_students.filter(id__in=FillOutResponse.objects.filter(form=form).values_list("student_id", flat=True)):
            writer.writerow([student_obj.roll_no, student_obj.first_name])

    elif download_type == "not_filled":
        filename = f"{form.title}_not_filled.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow(["Roll No", "Name"])
        for student_obj in form.assigned_students.exclude(id__in=FillOutResponse.objects.filter(form=form).values_list("student_id", flat=True)):
            writer.writerow([student_obj.roll_no, student_obj.first_name])

    return response

@api_view(['GET'])
@permission_classes([AllowAny])
def project_detail(request, project_id):
    try:
        project = get_object_or_404(Projects, id=project_id)
        serializer = ProjectSerializer(project, context={'request': request})

        # Include additional details for editing
        response_data = serializer.data

        # Add technologies
        response_data['technologies'] = []
        for tech in project.technologies.all():
            response_data['technologies'].append({
                'id': tech.id,
                'name': tech.name
            })

        # Add contributors
        response_data['contributors'] = []
        for contributor in project.contributors.all():
            response_data['contributors'].append({
                'id': contributor.id,
                'rollno': contributor.roll_no,
                'name': contributor.first_name,
                'last_name': contributor.last_name
            })

        return Response(response_data)
    except Exception as e:
        logging.error(f"Error in project_detail: {e}")
        return Response({'error': str(e)}, status=500)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users, 'user': request.user})

@user_passes_test(lambda u: u.is_superuser)
def admin_create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_superuser = 'is_superuser' in request.POST
        user = User(username=username, email=email, is_superuser=is_superuser, is_staff=is_superuser)
        user.set_password(password)
        user.save()
        messages.success(request, 'User created successfully!')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def admin_update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.is_superuser = 'is_superuser' in request.POST
        user.is_staff = user.is_superuser
        if request.POST.get('password'):
            user.set_password(request.POST['password'])
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_update_user.html', {'user_obj': user})

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

from django.http import HttpResponseBadRequest
@user_passes_test(lambda u: u.is_superuser)
def admin_create_student(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        roll_no = request.POST.get('roll_no', '')
        year = request.POST.get('year', 3)
        section = request.POST.get('section', 'A')
        dept = request.POST.get('dept', 'CSE')
        s = student(username=username, email=email, roll_no=roll_no, year=year, section=section, dept=dept)
        s.set_password(password)
        s.save()
        messages.success(request, 'Student created successfully!')
        return redirect('admin_dashboard')
    return HttpResponseBadRequest()
@user_passes_test(lambda u: u.is_superuser)
def admin_update_student(request, student_id):
    s = get_object_or_404(student, id=student_id)
    if request.method == 'POST':
        s.email = request.POST.get('email', s.email)
        s.roll_no = request.POST.get('roll_no', s.roll_no)
        s.year = request.POST.get('year', s.year)
        s.section = request.POST.get('section', s.section)
        s.dept = request.POST.get('dept', s.dept)
        if request.POST.get('password'):
            s.set_password(request.POST['password'])
        s.save()
        messages.success(request, 'Student updated successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_update_user.html', {'user_obj': s, 'is_student': True})
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_student(request, student_id):
    s = get_object_or_404(student, id=student_id)
    if request.method == 'POST':
        s.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('admin_dashboard')
    return HttpResponseBadRequest()
@user_passes_test(lambda u: u.is_superuser)
def admin_create_faculty(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        dept = request.POST.get('dept', 'CSE')
        default_year = request.POST.get('default_year', None)
        default_section = request.POST.get('default_section', 'A')
        f = Faculty(username=username, email=email, dept=dept, default_year=default_year, default_section=default_section)
        f.set_password(password)
        f.save()
        messages.success(request, 'Faculty created successfully!')
        return redirect('admin_dashboard')
    return HttpResponseBadRequest()
@user_passes_test(lambda u: u.is_superuser)
def admin_update_faculty(request, faculty_id):
    f = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        f.email = request.POST.get('email', f.email)
        f.dept = request.POST.get('dept', f.dept)
        f.default_year = request.POST.get('default_year', f.default_year)
        f.default_section = request.POST.get('default_section', f.default_section)
        if request.POST.get('password'):
            f.set_password(request.POST['password'])
        f.save()
        messages.success(request, 'Faculty updated successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_update_user.html', {'user_obj': f, 'is_faculty': True})
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_faculty(request, faculty_id):
    f = get_object_or_404(Faculty, id=faculty_id)
    if request.method == 'POST':
        f.delete()
        messages.success(request, 'Faculty deleted successfully!')
        return redirect('admin_dashboard')
    return HttpResponseBadRequest()
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import student, Faculty
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    students = student.objects.all()
    faculty = Faculty.objects.all()
    return render(request, 'admin_dashboard.html', {
        'students': students,
        'faculty': faculty,
        'user': request.user
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_superuser = 'is_superuser' in request.POST
        user = User(username=username, email=email, is_superuser=is_superuser, is_staff=is_superuser)
        user.set_password(password)
        user.save()
        messages.success(request, 'User created successfully!')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def admin_update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.is_superuser = 'is_superuser' in request.POST
        user.is_staff = user.is_superuser
        if request.POST.get('password'):
            user.set_password(request.POST['password'])
        user.save()
        messages.success(request, 'User updated successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin_update_user.html', {'user_obj': user})

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import JsonResponse
from .models import student, Certificate, Projects, PlacementOffer, LeetCode
import requests
import os

def is_coordinator(user):
    return hasattr(user, 'coordinatorrole') and user.coordinatorrole is not None

# FlexOn Dashboard Implementation
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
import traceback

def generate_orm_from_query(query):
    """
    Simple query-to-ORM mapping for common FlexOn queries.
    Returns a basic ORM string based on keywords in the query.
    """
    query_lower = query.lower()
    
    # Basic query patterns
    if 'top' in query_lower and 'leetcode' in query_lower:
        return "LeetCode.objects.order_by('-TotalProblems')[:10]"
    
    elif 'students' in query_lower and 'python' in query_lower and 'projects' in query_lower:
        return "student.objects.annotate(python_projects=Count('projects', filter=Q(projects__technologies__name__icontains='python'))).filter(python_projects__gt=0)"
    
    elif 'placement' in query_lower and 'offers' in query_lower:
        return "student.objects.annotate(offer_count=Count('placementoffer')).filter(offer_count__gt=0)"
    
    elif 'cloud' in query_lower and ('cert' in query_lower or 'certificate' in query_lower):
        return "Certificate.objects.filter(Q(source__icontains='cloud') | Q(title__icontains='cloud'))"
    
    elif 'placement' in query_lower and 'stats' in query_lower:
        return "student.objects.values('dept').annotate(total=Count('id'), placed=Count('placementoffer')).order_by('dept')"
    
    elif 'students' in query_lower and 'projects' in query_lower:
        return "student.objects.annotate(project_count=Count('projects')).filter(project_count__gt=0)"
    
    elif 'certificates' in query_lower:
        return "Certificate.objects.values('rollno__dept', 'category').annotate(count=Count('id')).order_by('rollno__dept')"
    
    elif 'leetcode' in query_lower:
        return "LeetCode.objects.select_related('rollno').order_by('-TotalProblems')"
    
    elif 'projects' in query_lower:
        return "Projects.objects.select_related('rollno').order_by('-id')"
    
    elif 'students' in query_lower:
        return "student.objects.all().order_by('roll_no')"
    
    else:
        # Default fallback
        return "student.objects.all()[:20]"


def _normalize_orm_line(orm_line: str, model_aliases: dict) -> str:
    """
    Rewrite '<Alias>.objects' -> '<actual>.objects' using ONLY the provided model_aliases.
    Adds singular/plural + case variants at runtime without mutating model_aliases.
    """
    if not orm_line:
        return orm_line

    import re
    
    # Build an expanded lookup without changing the original dict
    expanded = {}
    for alias, actual in model_aliases.items():
        variants = {alias, alias.lower(), alias.capitalize()}

        # add singular/plural variants
        if alias.endswith('s'):
            singular = alias[:-1]
            variants.update({singular, singular.lower(), singular.capitalize()})
        else:
            plural = alias + 's'
            variants.update({plural, plural.lower(), plural.capitalize()})

        for v in variants:
            expanded[v] = actual  # all map to the same "actual"

    # Replace ONLY tokens that are used as '<name>.objects'
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\.objects")

    def repl(m):
        name = m.group(1)
        actual = expanded.get(name) or expanded.get(name.lower())
        return f"{actual}.objects" if actual else m.group(0)

    return pattern.sub(repl, orm_line)


@csrf_exempt
def flexon_dashboard(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        clarification = ''
        results = []
        columns = []

        # Step 1: Generate ORM from query (returns a string)
        orm_line = generate_orm_from_query(query)

        # Step 2: Normalize model references using the GIVEN model_aliases (unchanged)
        model_aliases = {
            'Student': 'student',
            'Faculty': 'Faculty',
            'Projects': 'Projects',
            'Certificate': 'Certificate',
            'LeetCode': 'LeetCode',
            'Placement': 'Placement',
            'Technology': 'Technology',
        }
        orm_line = _normalize_orm_line(orm_line, model_aliases) if orm_line else None

        # Step 3: Safety check (read-only)
        unsafe_keywords = [
            'create', 'update', 'delete', 'save',
            'bulk_create', 'bulk_update', 'remove', 'clear', 'set'
        ]
        if not orm_line:
            clarification = "Couldn't generate a valid ORM query."
        elif any(kw in orm_line.lower() for kw in unsafe_keywords):
            clarification = "Unsafe ORM operation detected. Only read-only queries are allowed."
        else:
            try:
                # Step 4: Evaluate safely
                from .models import Faculty, Technology, Placement
                from django.db import models as django_models
                
                safe_globals = {
                    '__builtins__': {},  # lock down builtins
                    # models/modules
                    'models': django_models,
                    'Count': Count,
                    'Q': Q,
                    # model classes available to the ORM line
                    'student': student,
                    'Faculty': Faculty,
                    'Projects': Projects,
                    'Certificate': Certificate,
                    'LeetCode': LeetCode,
                    'Placement': Placement,
                    'Technology': Technology,
                    'PlacementOffer': PlacementOffer,
                }
                print(f"Executing ORM: {orm_line}")

                queryset = eval(orm_line, safe_globals, {})

                # Step 5: Normalize results to list-of-dicts and build columns
                from django.db.models import QuerySet
                
                def as_dicts_from_instances(qs):
                    model = qs.model
                    field_names = [f.name for f in model._meta.concrete_fields]
                    return list(qs.values(*field_names))

                if isinstance(queryset, dict):
                    # Aggregate: {'count': X, ...}
                    results = [queryset]
                    columns = list(queryset.keys())
                elif isinstance(queryset, (list, tuple)):
                    if queryset and isinstance(queryset[0], tuple):
                        # values_list / tuples -> map to col_1, col_2...
                        col_names = [f"col_{i+1}" for i in range(len(queryset[0]))]
                        results = [dict(zip(col_names, row)) for row in queryset[:50]]
                        columns = col_names
                    elif queryset and hasattr(queryset[0], '__class__'):
                        # list of model instances
                        model = queryset[0].__class__
                        field_names = [f.name for f in model._meta.concrete_fields]
                        results = [ {fn: getattr(obj, fn) for fn in field_names} for obj in queryset[:50] ]
                        columns = field_names
                    else:
                        results = []
                        columns = []
                elif isinstance(queryset, QuerySet):
                    # If caller already used .values(), don't double-process
                    try:
                        sample = queryset[:1]
                        # If it's a ValuesQuerySet, converting to list gives dicts
                        if sample and isinstance(list(sample)[0], dict):
                            results = list(queryset)[:50]
                        else:
                            results = as_dicts_from_instances(queryset)[:50]
                    except Exception:
                        # fallback to values() anyway
                        results = list(queryset.values())[:50]

                    columns = list(results[0].keys()) if results else []
                else:
                    # Any other scalar/object -> wrap it
                    results = [{"result": queryset}]
                    columns = ["result"]

            except Exception as e:
                clarification = f"Error executing ORM: {e}"
                traceback.print_exc()

        return JsonResponse({
            'clarification': clarification,
            'results': results,
            'columns': columns,
            'chart': None
        })

    return render(request, 'flexon_dashboard.html')
# flexapp/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum, Max, Min, Q
from .models import student, Faculty, Projects, Certificate, LeetCode, Placement, Technology, publications, certifications

MODEL_MAP = {
    "Student": student,
    "Faculty": Faculty,
    "Projects": Projects,
    "Certificate": Certificate,
    "LeetCode": LeetCode,
    "Placement": Placement,
    "Technology": Technology,
    "publications": publications,
    "certifications": certifications,
}
from django.apps import apps
from django.http import JsonResponse
from django.shortcuts import render

def query_builder(request):
    if request.method == "POST":
        import json
        config = json.loads(request.body.decode("utf-8"))

        model_name = config.get("model")
        filters = config.get("filters", [])

        if not model_name or model_name not in MODEL_MAP:
            return JsonResponse({"error": "Invalid model selected"}, status=400)

        Model = MODEL_MAP[model_name]
        qs = Model.objects.all()

        # Apply filters
        from django.db.models import Q
        q_obj = Q()
        for f in filters:
            field = f.get("field")
            operator = f.get("operator")
            value = f.get("value")
            if field and operator and value != "":
                lookup = f"{field}__{operator}"
                q_obj &= Q(**{lookup: value})
        qs = qs.filter(q_obj)

        results = list(qs.values()[:50])
        return JsonResponse({"results": results})

    # GET: load UI
    return render(request, "query_builder.html", {"models": list(MODEL_MAP.keys())})


def get_model_fields(request, model_name):
    """Return list of fields for a given model."""
    if model_name not in MODEL_MAP:
        return JsonResponse({"error": "Invalid model"}, status=400)

    Model = MODEL_MAP[model_name]
    fields = [f.name for f in Model._meta.get_fields()]
    return JsonResponse({"fields": fields})
