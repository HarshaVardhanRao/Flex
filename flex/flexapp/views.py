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
    if request.method == 'POST':
        if 'project-form' in request.POST:
            project_form = ProjectsForm(request.POST)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.rollno = request.user  
                project.save()
                return redirect('dashboard')
            else:
                print(project_form.errors) 
        elif 'certification-form' in request.POST:
            certification_form = ForignLanguagesForm(request.POST, request.FILES)
            if certification_form.is_valid():
                cert = certification_form.save(commit=False)
                cert.rollno = request.user 
                cert.save()
                return redirect('dashboard')
            else:
                print(certification_form.errors) 
    else:
        project_form = ProjectsForm()
        certification_form = ForignLanguagesForm()
    
    projects = Projects.objects.filter(rollno=request.user)
    Tech_certifications = ForignLanguages.objects.filter(rollno=request.user, category="TECHNICAL")
    For_lang = ForignLanguages.objects.filter(rollno=request.user, category="FOREIGN_LANGUAGE")

    
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

        total_problems = easy_count + medium_count + hard_count
        leet_user = LeetCode.objects.get_or_create(rollno = request.user)[0]
        leet_user.TotalProblems = total_problems
        leet_user.easy = easy_count
        leet_user.medium = medium_count
        leet_user.hard = hard_count
        leet_user.save()

    else:
        easy_count = medium_count = hard_count = 0 

    context = {
        'projects': projects,
        'Technical': Tech_certifications,
        'Foreign_languages': For_lang,
        'project_form': project_form,
        'certification_form': certification_form,
        'easy_count': easy_count,
        'medium_count': medium_count,
        'hard_count': hard_count,
    }

    return render(request, 'dashboard.html', context)

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectsForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.rollno = request.user 
            project.save()
            return redirect('dashboard') 
    else:
        form = ProjectsForm()
    return render(request, 'dashboard.html', {'form': form})

@login_required
def add_certification(request):
    if request.method == 'POST':
        form = ForignLanguagesForm(request.POST, request.FILES) 
        if form.is_valid():
            cert = form.save(commit=False)
            cert.rollno = request.user 
            cert.save()
            return redirect('dashboard')  
    else:
        form = ForignLanguagesForm()
    return render(request, 'dashboard.html', {'form': form})

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
        is_staff = role == 'staff'

        logging.debug(f"Received data: rollno={rollno}, password={password}, first_name={first_name}, role={role}")

        stu_email = f"{rollno}@mits.ac.in"
        
     
        try:
            user = student.objects.create_user(
                username=rollno,
                roll_no=rollno,
                is_staff=is_staff,
                first_name=first_name
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