from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .forms import ProjectsForm,LeetCodeForm,ForignLanguagesForm
from django.contrib.auth.decorators import login_required
from .models import *
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectsForm, LeetCodeForm, ForignLanguagesForm
from .models import Projects, ForignLanguages
import requests
from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    
    projects = Projects.objects.filter(rollno=request.user)
    Tech_certifications = ForignLanguages.objects.filter(rollno=request.user, category="Technical")
    For_lang = ForignLanguages.objects.filter(rollno=request.user, category="Foreign Language")

    
    username = request.user.leetcode_user
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

    context = {
        'projects': projects,
        'Technical': Tech_certifications,
        'Foreign_languages': For_lang,
        'easy_count': easy_count,
        'medium_count': medium_count,
        'hard_count': hard_count,
    }

    print(context)

    return render(request, 'dashboard.html', context)

@login_required
def create_project(request):
    if request.method == 'POST':
        rollno = request.user
        title = request.POST.get('project-name')
        description = request.POST.get('description')
        status = request.POST.get('status')
        github_link = request.POST.get('github')
        new_project = Projects(rollno=rollno, title=title, description=description, github_link=github_link)
        new_project.save()
        return redirect('dashboard')
    return render(request, 'dashboard.html')

@login_required
def add_certification(request):
    if request.method == 'POST':
        print("POST")
        rollno = request.user
        course_type = request.POST.get('type')
        title = request.POST.get('course-name')
        source = request.POST.get('provider')
        status = request.POST.get('status')
        course_link = request.POST.get('course-link')
        new_course = ForignLanguages(rollno=rollno, title=title, source=source, course_link=course_link, category=course_type)
        new_course.save()
        return redirect('dashboard')
    return render(request, 'dashboard.html')

def CustomLogin(request):
    if request.method == 'GET':
        rollno = request.GET.get('rollno')
        password = request.GET.get('password')
        print(rollno, password)
        user = authenticate(username=rollno, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

@login_required
def CustomLogout(request):
    logout(request)
    return redirect('/')

logging.basicConfig(level=logging.DEBUG)

def register(request):
    if request.method == 'POST':
        rollno = request.POST.get('rollno')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        role = request.POST.get('role')
        deptt = request.POST.get('dept')
        section = request.POST.get('section')
        is_staff = role == 'staff'

        logging.debug(f"Received data: rollno={rollno}, password={password}, first_name={first_name}, role={role}")

        stu_email = f"{rollno}@mits.ac.in"
        
     
        try:
            user = student.objects.create_user(
                username=rollno,
                roll_no=rollno,
                is_staff=is_staff,
                first_name=first_name,
                dept=deptt,
                section=section,
                leetcode_user=rollno,
            )
            logging.debug(f"User created: {user}")

            if not user.is_staff:
                user.email = stu_email

            
            user.set_password(password)
            user.save()
            logging.debug(f"User saved: {user}")

            
            authenticated_user = authenticate(username=rollno, password=password)
            logging.debug(f"Authenticated user: {authenticated_user}")

            if authenticated_user is not None:
                login(request, authenticated_user)
                logging.debug(f"User logged in: {authenticated_user}")
                return redirect('dashboard')
            else:
                logging.error("Authentication failed.")
                return redirect('login')

        except Exception as e:
            logging.error(f"Error during registration: {e}")
            return render(request, 'register.html', {'error': str(e)})

    return render(request, 'register.html')