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
            return redirect(request,dashboard)
    return render(request, 'login.html')

def CustomLogout(request):
    logout(request)
    return redirect(request, login)

def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
        return redirect(request, login)