from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout

def CustomLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

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
        rollno = request.POST.get('rollno')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        is_staff = True if request.POST.get('role') == 'staff' else False
        user = student.objects.create_user(roll_no=rollno,email=email,is_staff=is_staff,first_name=first_name)
        user.set_password(password)
        user.save()
        return redirect('login')
    return render(request, 'register.html')