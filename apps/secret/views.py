from django.shortcuts import render, redirect, HttpResponse
from .models import User, Secret
from django.contrib import messages
from django.db.models import Count
import bcrypt

def index(request):
    return render(request, "index.html")

def success(request):
    secret = Secret.objects.all().order_by("-created_at")
    arr = []
    for i in secret:
        for j in i.likes.all():
            if j.id == request.session['uid']:
                arr.append(i.id)
    print arr
    context = {
    "secret" : secret[:5],
    "likearr" : arr
    }
    return render(request, "secret.html", context)

def popsecret(request):
    secret = Secret.objects.all().annotate(numLikes = Count('likes')).order_by('-numLikes')
    arr = []
    for i in secret:
        for j in i.likes.all():
            if j.id == request.session['uid']:
                arr.append(i.id)
    context = {
    "secret" : secret,
    "likearr" : arr
    }
    return render(request, "mostpop.html", context)

def register(request):
    fname = str(request.POST['first_name'])
    lname = str(request.POST['last_name'])
    email = str(request.POST['email'])
    pwd = request.POST['password'].encode()
    conpwd = request.POST['confirm_password'].encode()
    context = {
    "fname" : fname,
    "lname" : lname,
    "email" : email,
    "pwd" : pwd,
    "conpwd" : conpwd
    }
    if  User.objects.all().filter(email = email):
        messages.add_message(request, messages.INFO, "Email already exists! Please login")
        return redirect('/')
    error = User.objects.validate(context)
    if error:
        for ele in error:
            messages.add_message(request, messages.ERROR, ele)
        return redirect('/')
    else:
        hashedpwd = bcrypt.hashpw(pwd, bcrypt.gensalt())
        user = User.objects.create(first_name = fname, last_name = lname, email = email, password = hashedpwd)
        request.session['uid'] = user.id
        request.session['uname'] = user.first_name
        return redirect('/success')

def login(request):
    email = str(request.POST['email'])
    pwd = request.POST['password'].encode()
    user = User.objects.all().filter(email = email)
    if  not user:
        messages.add_message(request, messages.INFO, "Email doesn't exist! Please register")
        return redirect('/')
    else:
        if user[0].password != bcrypt.hashpw(pwd, (user[0].password).encode()):
            messages.add_message(request, messages.INFO, "Invalid password")
            return redirect('/')
        else:
            request.session['uid'] = user[0].id
            request.session['uname'] = user[0].first_name
            return redirect('/success')

def secret(request):
    secret = str(request.POST['secret'])
    user = User.objects.get(id = request.session['uid'])
    Secret.objects.create(secret = secret, user = user)
    return redirect('/success')

def like(request, id):
    this_user = User.objects.get(id = request.session['uid'])
    this_secret = Secret.objects.get(id = id)
    this_secret.likes.add(this_user)
    return redirect('/success')

def delete(request,id):
    dele = Secret.objects.get(id = id)
    dele.delete()
    return redirect('/success')

def logout(request):
    request.session.clear()
    return redirect('/')
