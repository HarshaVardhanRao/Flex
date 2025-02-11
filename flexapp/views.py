from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import ProjectsForm, LeetCodeForm, ForignLanguagesForm
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Projects, ForignLanguages, student, LeetCode, Faculty
import requests
from django.http import HttpResponse, JsonResponse
import requests
import json
from django.core import serializers
import pandas as pd
from django.http import HttpResponse
from django.core.mail import send_mail
import random
from flex import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

logging.basicConfig(level=logging.DEBUG)

def getStudentDetails(student):
    try:
        projects = Projects.objects.filter(rollno=student)
        Tech_certifications = ForignLanguages.objects.filter(rollno=student, category="Technical")
        For_lang = ForignLanguages.objects.filter(rollno=student, category="Foreign Language")
        
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

@login_required
def create_project(request):
    try:
        if request.method == 'POST':
            rollno = request.user
            title = request.POST.get('project-name')
            description = request.POST.get('description')
            year_and_sem = request.POST.get('year-and-sem')
            status = request.POST.get('status')
            github_link = request.POST.get('github')
            new_project = Projects(rollno=rollno, title=title, description=description, github_link=github_link, year_and_sem=year_and_sem, status=status)
            new_project.save()
            return redirect('dashboard')
        return render(request, 'dashboard.html')
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
            year_and_sem = request.POST.get('year-and-sem')
            source = request.POST.get('provider')
            status = request.POST.get('status')
            course_link = request.POST.get('course-link')
            new_course = ForignLanguages(rollno=rollno, title=title, source=source, course_link=course_link, category=course_type, year_and_sem=year_and_sem)
            new_course.save()
            return redirect('dashboard')
        return render(request, 'dashboard.html')
    except Exception as e:
        logging.error(f"Error in add_certification: {e}")
        return HttpResponse("An error occurred.")

def CustomLogin(request):
    try:
        if request.user.is_authenticated:
            if request.user.type() == "student":
                return redirect('dashboard')
            if request.user.type() == "Faculty":
                return redirect('faculty')
        if request.method == 'POST':
            rollno = request.POST.get('rollno')
            password = request.POST.get('password')
            user = authenticate(request=request, username=rollno, password=password)
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
import smtplib
from email.mime.text import MIMEText
def send_otp(email):
    try:
        otp = random.randint(100000, 999999)
        logging.debug(f"Generated OTP: {otp}")
        sender_email = "webclubmits@gmail.com"
        sender_password = "geby ycow vxgn ekxu"
        smtp_server = "smtp-mail.outlook.com"
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
    except Exception as e:
        logging.error(f"Error in send_otp: {e}")
        return None

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

from django.db.models import Count
# @login_required
def faculty(request):
    try:
        studentData = list(student.objects.filter(is_superuser=False).annotate(project_count=Count('Projects'),foreign_language_count=Count('ForeignLanguages')    ).values("roll_no", "first_name", "dept", "year", "section", "studentrollno__TotalProblems", "Projects", "ForeignLanguages"))
        return render(request, 'faculty_dashboard.html', {'studentData': studentData})
    except Exception as e:
        logging.error(f"Error in faculty: {e}")
        return HttpResponse("An error occurred.")

def edit_project(request):
    try:
        if request.method == 'POST':
            primary_key = request.POST.get('id')
            title = request.POST.get('project-name')
            description = request.POST.get('description')
            year_and_sem = request.POST.get('year-and-sem')
            print(year_and_sem)
            status = request.POST.get('status')
            github_link = request.POST.get('github')
            project = Projects.objects.get(id=primary_key)
            project.title = title
            project.description = description
            project.year_and_sem = year_and_sem
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
            year_and_sem = request.POST.get('year-and-sem')
            title = request.POST.get('course-name')
            course_link = request.POST.get('course-link')
            project = ForignLanguages.objects.get(id=primary_key)
            project.source = source
            project.title = title
            project.year_and_sem = year_and_sem
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
        project = ForignLanguages.objects.get(id=primary_key)
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

def download_request(request):
    try:
        list = request.body
        list = json.loads(list)
        students = student.objects.filter(roll_no__in=list)
        data = []
        for stu in students:
            leetcode = LeetCode.objects.get(rollno=stu)
            technical = ForignLanguages.objects.filter(rollno=stu, category="Technical")
            foreign = ForignLanguages.objects.filter(rollno=stu, category="Foreign Language")
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
            otp = send_otp(f"{user.email}")
            request.session['rollno'] = rollno
            request.session['otp'] = otp
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
        
        if 'mobile' in request.POST:
            section = request.POST.get("mobile")
            if section and section != user.phone:
                user.phone = section
                updated_fields['phone'] = section
        
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
