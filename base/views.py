from email import message
from multiprocessing import context
from pickle import NONE
from pickletools import read_uint1
from pydoc import pager
from pydoc_data.topics import topics
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Room,Topic,Message,User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .forms import RoomForm,UserForm,MyUserCreationForm


from django.db.models import Q

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method=='POST':
        email=request.POST.get('email').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exists')
        
        user =authenticate(request,email=email,password=password)
        if user is not None:
            messages.success(request, 'Profile details updated.')
            login(request,user)
            return redirect('home')
        else :
            messages.error(request, 'Username or password is invalid')

    context={'page':page}
    return render(request,'base/login_register.html',context)

def logoutuser(request):
    logout(request)
    return redirect('home')

def registeruser(request):
    page='register'
    form=MyUserCreationForm()
    if request.method=='POST':
        form=MyUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else :
            messages.error(request,'an error occured')



    context={'page':page,'form':form}
    return render(request,'base/login_register.html',context)


def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    topics=Topic.objects.all()[0:4]
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context={
        'rooms':rooms,
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages,
    }
    return render(request,'base/home.html',context)


def room(request,pk):
    room=Room.objects.get(id=pk)
    #get the meaasges of this particular room
    room_messages=room.message_set.all()
    participants=room.participants.all()
    if request.method=='POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST['body']
        )
        #add this user as a participant in the room
        room.participants.add(request.user)
        # message.save()
        return redirect('room',pk=room.id)

    context={
        'room':room,
        'room_messages':room_messages,
        'participants':participants,
    }
    return render(request,'base/room.html',context)


def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method=='POST':
        topic_name=request.POST['topic']
        #if a new topic is entered whcich is not in the db then created will be true and return a new topic obj
        #if the topic already exists then created will be false and the topci obj is returend
        topic,created=Topic.objects.get_or_create(name=topic_name) ##

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST['name'],
            description=request.POST['description'],
        )
        return redirect('home')
     
    context={'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    topics=Topic.objects.all()
    form=RoomForm(instance=room) 
    if request.user!=room.host:
        return HttpResponse('Not allowed here')

    if request.method=='POST':
        topic_name=request.POST['topic']
        topic,created=Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST['name']
        room.topic=topic
        room.description=request.POST['description']
        room.save()
        return redirect('home')

    context={'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user!=room.host:
        return HttpResponse('Not allowed here')

    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user!=message.user:
        return HttpResponse('Not allowed here')

    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)
    if request.method =='POST':
        form=UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)

    context={'form':form}
    return render(request,'base/update-user.html',context)

def topicsPage(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    topics=Topic.objects.filter(name__icontains=q)
    context={'topics':topics}
    return render(request,'base/topics.html',context)

def activityPage(request):
    room_messages=Message.objects.all()
    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)