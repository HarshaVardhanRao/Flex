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
