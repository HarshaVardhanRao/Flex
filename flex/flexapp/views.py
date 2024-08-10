from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .forms import ProjectForm,LeetCodeForm,ForignLanguageForm
from django.contrib.auth.decorators import login_required
from .models import *
import logging

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

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
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


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.student = request.user.student
            project.save()
            return redirect('dashboard') 
    else:
        form = ProjectForm()
    return render(request, 'dashboard.html', {'form': form})

@login_required
def add_certification(request):
    if request.method == 'POST':
        form = ForignLanguageForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.student = request.user.student
            cert.save()
            return redirect('dashboard')  
    else:
        form = ForignLanguageForm()
    return render(request, 'dashboard.html', {'form': form})

@login_required
def updateLeetCode(request):#subject to change,if we pass int in URL , view will change
    if request.method == 'POST':
        form = LeetCodeForm(request.POST)
        if form.is_valid():
            Leet = form.save(commit=False)
            Leet.student = request.user.student
            Leet.save()
            return redirect('dashboard') 
    else:
        form = LeetCodeForm()
    return render(request, 'dashboard.html', {'form': form})

@login_required
def UpdateLeet(request,count):
    Leet = LeetCode.objects.get(studenr=request.user)
    Leet.TotalProblems = count
    Leet.save()
    return redirect('dashboard')