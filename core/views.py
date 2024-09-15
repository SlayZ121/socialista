from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, likepost, followers
from itertools import chain
import random

# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_follow=[]
    feed = []

    user_f= followers.objects.filter(follower=request.user.username)

    for users in user_f:
        user_follow.append(users.user)

    for usernames in user_follow:
        feed_list=Post.objects.filter(user=usernames)
        feed.append(feed_list)

    feed_list = list(chain(*feed))

    #user suggestions
    allusers=User.objects.all()
    user_following=[]

    for user in user_f:
        user_list = User.objects.get(username=user.user)
        user_following.append(user_list)

    new_suggest = [x for x in list(allusers) if (x not in list(user_following))]
    current_user=User.objects.filter(username=request.user.username)
    final_suggestion = [x for x in list(new_suggest) if ( x not in list(current_user))]
    random.shuffle(final_suggestion)
    
    username_profile = []
    username_profile_list = []

    for user in final_suggestion:
        username_profile.append(user.id)
    
    for ids in username_profile:
        profile_list = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_list)

    suggestionslist = list(chain(*username_profile_list))




    posts = Post.objects.all()



    return render(request,'index.html',{'user_profile' : user_profile,'posts': feed_list, 'rec' : suggestionslist[:4]})

@login_required(login_url='signin')
def profile(request,pk):
    user_object=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user_object)
    user_posts=Post.objects.filter(user=pk)
    user_posts_length= len(user_posts)
    follower = request.user.username
    user= pk

    if followers.objects.filter(follower=follower,user = user).first():
        button_text='Unfollow'
    else:
        button_text='Follow'

    user_followers=len(followers.objects.filter(user=pk))
    user_following=len(followers.objects.filter(follower=pk))
    context={
        'user_object' : user_object,
        'user_profile': user_profile,
        'user_posts' : user_posts,
        'user_post_length': user_posts_length,
        'button_text': button_text,
        'user_followers' : user_followers,
        'user_following': user_following,
    }

    return render(request,'profile.html',context)


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user= user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile=[]
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists= Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request,'search.html',{"user_profile" : user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image= request.FILES.get('image_upload')
        caption= request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')


    else:
        return redirect('/')

@login_required(login_url='signin')
def like(request):
    username= request.user.username
    postid= request.GET.get('post_id')
    post= Post.objects.get(id=postid)

    like_filter=likepost.objects.filter(postid=postid,username=username).first()


    if like_filter == None:
        new_like=likepost.objects.create(postid=postid,username=username)
        new_like.save()
        post.likes=post.likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.likes=post.likes-1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower=request.POST['follower']
        user=request.POST['user']

        if followers.objects.filter(follower=follower,user=user).first():
            delete_follower=followers.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = followers.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+user)


    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile=Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio=request.POST['bio']
            location=request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image= request.FILES.get('image')
            bio=request.POST['bio']
            location=request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')




    return render(request,'setting.html',{'user_profile':user_profile})

def signup(request):

    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password2=request.POST['password2']

        if password==password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Another user with this email already exists!')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username already exists!')
                return redirect('signup')
            else:
                user=User.objects.create_user(username=username,email=email,password=password)
                user.save()

                #log user in and redirect to settings page
                user_login=auth.authenticate(username=username,password=password)
                auth.login(request,user_login)


                #create a profile object for the new user
                user_model=User.objects.get(username=username)
                new_profile=Profile.objects.create(user=user_model,id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
            

        else:
            messages.info(request,'Passwords do not match!')
            return redirect('signup')

    

    else:
       return render(request,'signup.html')
 

def signin(request):
    
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Invalid login credentials')
            return redirect('/signin')


    else:
       return render(request,'signin.html')
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

