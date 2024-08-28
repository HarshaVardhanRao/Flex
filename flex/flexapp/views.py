from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .forms import ProjectsForm,LeetCodeForm,ForignLanguagesForm
from django.contrib.auth.decorators import login_required
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProjectsForm, LeetCodeForm, ForignLanguagesForm
from .models import Projects, ForignLanguages, student, LeetCode
import requests
from django.http import HttpResponse, JsonResponse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from django.core import serializers
import pandas as pd
from django.http import HttpResponse

@login_required
def dashboard(request):
    
    projects = Projects.objects.filter(rollno=request.user)
    Tech_certifications = ForignLanguages.objects.filter(rollno=request.user, category="Technical")
    For_lang = ForignLanguages.objects.filter(rollno=request.user, category="Foreign Language")
    
    context = {
        'projects': serializers.serialize('json', projects),
        'Technical': serializers.serialize('json', Tech_certifications),
        'Foreign_languages': serializers.serialize('json', For_lang),
        'easy_count': 20,
        'medium_count': 35,
        'hard_count': 7,
    }

    #print(context)

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
        leetcode_user = request.POST.get('leetcode_user')

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
                leetcode_user=leetcode_user,
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

def faculty(request):
    studentData = student.objects.all()
    return render(request, 'faculty_dashboard.html',{'studentData': serializers.serialize('json', studentData)})


def edit_project(request):
    if request.method == 'POST':
        primary_key = request.POST.get('id')
        title = request.POST.get('project-name')
        description = request.POST.get('description')
        status = request.POST.get('status')
        github_link = request.POST.get('github')
        print(title, description, status, github_link)
        project = Projects.objects.get(id=primary_key)
        project.title = title
        project.description = description
        project.status = status
        project.github_link = github_link
        project.save()
        return redirect('dashboard')

def edit_certification(request):
    if request.method == 'POST':
        primary_key = request.POST.get('id')
        source = request.POST.get('provider')
        title = request.POST.get('course-name')
        course_link = request.POST.get('course-link')
        project = ForignLanguages.objects.get(id=primary_key)
        project.source = source
        project.title = title
        project.course_link = course_link
        project.save()
        return redirect('dashboard')


def delete_project(request,primary_key):
    project = Projects.objects.get(id=primary_key)
    project.delete()
    return redirect('dashboard')

def delete_certification(request,primary_key):
    project = ForignLanguages.objects.get(id=primary_key)
    project.delete()
    return redirect('dashboard')


def leetcode_request(request):
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
    leetcode_user, created = LeetCode.objects.get_or_create(rollno=request.user)
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

def download_request(request):
    list = request.body
    list = json.loads(list)
    students = student.objects.filter(id__in=list)
    print(students)
    data = []
    for stu in students:
        leetcode = LeetCode.objects.get(rollno=stu)
        technical = ForignLanguages.objects.filter(rollno=stu, category="Technical")
        foreign = ForignLanguages.objects.filter(rollno=stu, category="Foreign Language")
        projects = Projects.objects.filter(rollno=stu)
        data.append({
            'Roll No': stu.roll_no,
            'student Name': stu.first_name,
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
