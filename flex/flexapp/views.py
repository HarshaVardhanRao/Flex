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

@login_required
def dashboard(request):
    if request.method == 'POST':
        if 'project-form' in request.POST:
            project_form = ProjectsForm(request.POST)  # Ensure 'ProjectsForm' matches form class in forms.py
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.rollno = request.user  # Assuming `request.user` is the student
                project.save()
                return redirect('dashboard')
            else:
                print(project_form.errors)  # For debugging
        elif 'certification-form' in request.POST:
            certification_form = ForignLanguagesForm(request.POST, request.FILES)  # Include request.FILES for file uploads
            if certification_form.is_valid():
                cert = certification_form.save(commit=False)
                cert.rollno = request.user  # Assuming `request.user` is the student
                cert.save()
                return redirect('dashboard')
            else:
                print(certification_form.errors)  # For debugging
    else:
        project_form = ProjectsForm()
        certification_form = ForignLanguagesForm()

    context = {
        'project_form': project_form,
        'certification_form': certification_form,
    }

    return render(request, 'dashboard.html', context)

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectsForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.rollno = request.user  # Ensure `rollno` is set to `request.user`
            project.save()
            return redirect('dashboard') 
    else:
        form = ProjectsForm()
    return render(request, 'dashboard.html', {'form': form})

@login_required
def add_certification(request):
    if request.method == 'POST':
        form = ForignLanguagesForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            cert = form.save(commit=False)
            cert.rollno = request.user  # Ensure `rollno` is set to `request.user`
            cert.save()
            return redirect('dashboard')  
    else:
        form = ForignLanguagesForm()
    return render(request, 'dashboard.html', {'form': form})

def CustomLogin(request):
    if request.method == 'POST':
        rollno = request.POST.get('rollno')
        password = request.POST.get('password')
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
        
        # Create the user
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
