from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
import logging
from django.contrib.auth.decorators import login_required
from .models import Projects, Certificate, student, LeetCode, Faculty,FillOutForm, FillOutField, student
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

def index(request):
    if request.user.is_authenticated:
        print(request.user)
        if request.user.type() == "student":                
            return redirect('dashboard')
        if request.user.type() == "Faculty":
            return redirect('faculty')
    print("redirecting to Login")
    return redirect('login')

logging.basicConfig(level=logging.DEBUG)

def getStudentDetails(student):
    try:
        # Ensure we are querying the correct model field
        # projects = Projects.objects.filter(contributors=student)  # Updated line
        projects = Projects.objects.prefetch_related("technologies").filter(contributors=student)
        
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
            tech_names = request.POST.getlist('technologies')

            contributors_ids = [id.strip() for id in contributors_ids if id.strip()]
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
            if hasattr(request.user, 'student'):
                new_project.contributors.add(request.user.student)

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
            if request.user.type() == "student":
                return redirect('dashboard')
            if request.user.type() == "Faculty":
                return redirect('faculty')
            if request.user.is_superuser:
                return redirect('admin')

            
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
    if request.user.type() == "Faculty":
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
# @login_required
def faculty(request):
    try:
        from .models import student  # or whatever your model is called

        studentData = list(
            student.objects.filter(is_superuser=False)
            .annotate(
                project_count=Count('projects', distinct=True),
                certificate_count=Count('certificates', distinct=True)
            )
            .values(
                'roll_no', 'first_name', 'dept', 'year', 'section',
                'studentrollno__TotalProblems',  # double-check this name
                'project_count', 'certificate_count'
            )
        )
        return render(request, 'faculty_dashboard.html', {'studentData': studentData})

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
def edit_project(request):
    try:
        if request.method == 'POST':
            primary_key = request.POST.get('id')
            title = request.POST.get('project-name')
            description = request.POST.get('description')
            status = request.POST.get('status')
            github_link = request.POST.get('github')
            project = Projects.objects.get(id=primary_key)
            project.title = title
            project.description = description
            project.status = status
            project.github_link = github_link
            project.save()
            return redirect('dashboard')
    except Exception as e:
        logging.error(f"Error in edit_project: {e}")
        return HttpResponse("An error occurred.")

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
        return redirect('dashboard')
    except Exception as e:
        logging.error(f"Error in delete_project: {e}")
        return HttpResponse("An error occurred.")

def delete_certification(request, primary_key):
    try:
        project = Certificate.objects.get(id=primary_key)
        project.delete()
        return redirect('dashboard')
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


def form_detail_view(request, form_id):
    form = get_object_or_404(FillOutForm, id=form_id)
    assigned_students = form.assigned_students.all()
    responses = FillOutResponse.objects.filter(form=form)

    responded_student_ids = responses.values_list('student_id', flat=True)
    responded_students = assigned_students.filter(id__in=responded_student_ids)
    non_responded_students = assigned_students.exclude(id__in=responded_student_ids)

    context = {
        'form': form,
        'responses': responses,
        'responded_students': responded_students,
        'non_responded_students': non_responded_students,
        'responded_count': responded_students.count(),
        'not_responded_count': non_responded_students.count(),
        'total': assigned_students.count(),
    }

    return render(request, 'dashboard/form_detail.html', context)


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


