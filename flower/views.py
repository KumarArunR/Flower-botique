from django.shortcuts import render,redirect
from django.http import HttpResponse
from flower.models import signup
from shop.models import product

def home(request):
    return render(request,'flower/home.html',{'msg':'welcome to bloom room'})
def contact(request):
    return render(request,'flower/contact.html')
def about(request):
    return render(request,'flower/about.html')




def signin_v(request):
    if request.method =="POST":
        user=request.POST['uname']
        pwd=request.POST['pass']
        cpwd=request.POST['cpass']
        mail=request.POST['email']
        if signup.objects.filter(username=user).exists() or signup.objects.filter(email=mail).exists():
               return render(request,'flower/home.html',{'msg':'username or mail exist','page':'SIGNUP NOW'})
        else:
            if(pwd==cpwd):
                   signup.objects.create(username=user,password=pwd,email=mail)
                   return render(request,'flower/home.html',{'msg':'registeredsuccessfully'})
            else:
                   return render(request,'flower/home.html',{'msg':'password mismatch','uname':request.POST['uname'],'email':mail})

    else:
        return HttpResponse("unable to process ur request")

def login_v(request):
    if request.method =='POST':
        user=request.POST['uname']
        pwd=request.POST['pass']
        if signup.objects.filter(username=user,password=pwd).exists():
             t=product.objects.all()
             request.session['user']=user
             request.session['admin']=0
             return redirect('/show')

        else:
               return render(request,'flower/home.html',{'msg':'username or password mismatch'})
    else:
        return render(request,'flower/login.html')

def reset(request):
    return render(request,'flower/reset.html',{'page':'RESET UR PASSWORD'})
def resv(request):
    if request.method=="POST":
        user=request.POST['uname']
        pwd=request.POST['pass']
        cpwd=request.POST['cpass']
        mail=request.POST['email']
        if signup.objects.filter(username=user,email=mail):
            if(pwd==cpwd):
                signup.objects.filter(username=user).update(password=pwd)
                return render(request,'flower/login.html',{'msg':'password reset successfully','page':"LOGIN"})
            else:
                return render(request,'flower/reset.html',{'msg':'password mismatch','page':'RESET UR PASSWORD'})
        else:
                return render(request,'flower/reset.html',{'msg':'username or email id mismatch','page':'RESET UR PASSWORD'})
    

# Create your views here.
