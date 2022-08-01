from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm



def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)
        if user != None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or Password does not exist")
    context = {'page': page}
    return render(request, 'base/login_register.html', context=context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    context = {'page': page,
               'form': form}
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Add error occurred during registration')
    return render(request, 'base/login_register.html', context=context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(description__icontains=q))
    topics = Topic.objects.all().annotate(rooms_count=Count('room')).order_by('-rooms_count')[:3]
    room_count = rooms.count()
    messages_room = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms,
               'topics': topics,
               'room_count': room_count,
               'messages_room': messages_room,
               'room_count': Room.objects.count()}
    return render(request, 'base/home.html', context=context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    messages_room = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        message_user = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room,
               'messages_room': messages_room,
               'participants': participants}
    return render(request, 'base/room.html', context=context)



def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    messages_room = user.message_set.all()
    topics = Topic.objects.all().annotate(rooms_count=Count('room')).order_by('-rooms_count', 'name')[:3]
    context = {'user': user,
               'rooms':rooms,
               'messages_room': messages_room,
               'topics': topics,
               'room_count': Room.objects.count()}
    return render(request, 'base/profile.html', context=context)


@login_required(login_url=reverse_lazy('login'))
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     form.save()
        #     return redirect('home')
    context = {'form': form,
               'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url=reverse_lazy('login'))
def updateRoom(request, pk):
     room = Room.objects.get(id=pk)
     form = RoomForm(instance=room)
     topics = Topic.objects.all()

     if request.user != room.host:
         return HttpResponse('You are not allowed here!!!')

     if request.method == "POST":
         topic_name = request.POST.get('topic')
         topic, created = Topic.objects.get_or_create(name=topic_name)
         room.name = request.POST.get('name')
         room.topic = topic
         room.description = request.POST.get('description')
         room.save()
         return redirect('home')
         # form = RoomForm(request.POST, instance=room)
         # if form.is_valid():
         #     form.save()
         #     return redirect('home')
     context = {'form':form,
                'topics': topics,
                'room': room}
     return render(request, 'base/room_form.html', context)


@login_required(login_url=reverse_lazy('login'))
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!!')

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url=reverse_lazy('login'))
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!!')

    if request.method == "POST":
        message.delete()
        if not request.user.message_set.filter(room=message.room).exists():
            message.room.participants.remove(request.user)
        if 'next' in request.GET.keys():
            return redirect(request.GET.get('next'))
        return redirect('room', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj':message})


@login_required(login_url=reverse_lazy('login'))
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(instance=user, files=request.FILES, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context=context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    if q:
        topics = Topic.objects.filter(Q(name__icontains=q))
    else:
        topics = Topic.objects.all().annotate(rooms_count=Count('room')).order_by('-rooms_count', 'name')
    context = {'topics': topics,
               'room_count': Room.objects.count()}
    return render(request, 'base/topics.html', context=context)


def activityPage(request):
    messages_room = Message.objects.all()
    context = {'messages_room': messages_room}
    return render(request, 'base/activity.html', context=context)