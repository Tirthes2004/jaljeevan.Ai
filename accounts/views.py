from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def demo(request):
    return render(request,'demo.html')



# Register user
def registerUser(request):  
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            messages.error(request,"All fields required!")
            return redirect('registerUser')
        
        elif(password == confirm_password):
            if(User.objects.filter(email=email).exists()):
                messages.info(request,"Email already exist, Try with another")
                return redirect('registerUser')
            elif(User.objects.filter(username=username).exists()):
                messages.info(request,'Username already exist, Try with another')
                return redirect('registerUser')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()
                login(request,user)
                messages.success(request,'Account Created Succesfully')
                return redirect('loginUser')
        else:
            messages.info(request,"Password Mismatched")
            return redirect('registerUser')

    else:
        return render(request,'accounts/registerUser.html')

#  Login
def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"Succesfully Logged In")
            return redirect('demo')
        else:
            messages.error(request,"Credential Mismatched!!!")
            return redirect('loginUser')
        
    return render(request,'accounts/loginUser.html')

#  LogOut
def logoutUser(request):
    logout(request)
    messages.success(request,"Successfully Logged Out!!!")
    return redirect('demo')
