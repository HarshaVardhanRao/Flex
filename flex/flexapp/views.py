from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .forms import ProjectForm,LeetCodeForm,ForignLanguageForm
from django.contrib.auth.decorators import login_required
from .models import *

def CustomLogin(request):
    if request.method == 'POST':
        rollno = request.POST.get('rollno').lower()
        password = request.POST.get('password')
        user = authenticate(roll_no=rollno, password=password)
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

def  register(request):
    if request.method == 'POST':
        rollno = request.POST.get('rollno').lower()
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        is_staff = True if request.POST.get('role') == 'staff' else False
        user = student.objects.create_user(roll_no=rollno,email=email,is_staff=is_staff,first_name=first_name)
        user.set_password(password)
        user.save()
        return redirect('login')
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