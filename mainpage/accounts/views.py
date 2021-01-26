from django.shortcuts import render, redirect

from django.contrib.auth.models import User, Group
from django.contrib import auth

# SMTP 관련 인증
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token

from .rand import rand_password
# Create your views here.
def findchangepw(request):
    if request.method == 'POST':
        username = request.POST['username']
        exist = User.objects.filter(username=username).first()
        if (exist and 'getnew' in request.POST):
            tmp_password = rand_password()
            exist.set_password(tmp_password)
            exist.pw_changing=True
            exist.save()
            message = render_to_string('accounts/password_email.html', {
                'user' : exist,
                'tmp_password' : tmp_password
            })
            mail_title = "SNU Lecture Subtitle : Temporary password"
            mail_to = request.POST["username"] + '@snu.ac.kr'
            email = EmailMessage(mail_title, message, to=[mail_to])
            email.send()
            return render(request, 'accounts/findchangepw.html', {'error' : 'Check email for Temporary password'})
        else:
            return render(request, 'accounts/findchangepw.html', {'error' : 'User not found'})
    return render(request, 'accounts/findchangepw.html')


def changepw(request):
    if request.method == 'POST':
        username = request.POST['username']
        oldpassword = request.POST['password0']
        newpassword = request.POST['password1']

        exist = User.objects.filter(username=username).first()

        if (exist and 'setnew' in request.POST):
            user = auth.authenticate(request, username=username, password=oldpassword)
            if user is not None:
                if request.POST['password1'] != request.POST['password2']:
                    return render(request, 'accounts/changepw.html', {'error': 'Check the new password again'})
                else:
                    exist.set_password(newpassword)
                    exist.pw_changing=False
                    exist.save()
                    user.set_password(newpassword)
                    user.pw_changing=False
                    user.save()
                    return render(request, 'accounts/login.html', {'error': 'Password resetted'})
            else:
                return render(request, 'accounts/changepw.html', {'error': 'Temporary password incorrect'})
        else:
            return render(request, 'accounts/changepw.html', {'error': 'User not found'})
    return render(request, 'accounts/changepw.html')



def signup(request):
    if request.method == 'POST':
        exist = User.objects.filter(username=request.POST['username']).first()
        if exist:
            return render(request, 'accounts/signup.html', {'error': 'You already have an account'})

        elif request.POST['username']:
            if request.POST['password1'] != request.POST['password2']:
                return render(request, 'accounts/signup.html', {'error': 'Check the password again'})
            user = User.objects.create_user(username=request.POST['username'], 
                    password=request.POST['password1'], 
                    email=request.POST['username'] + '@snu.ac.kr')
            user.is_active = False
            user.is_staff = False
            user.is_superuser = False
            user.save()
            current_site = get_current_site(request) 
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_title = "SNU Lecture Subtitle : Account activation"
            mail_to = request.POST["username"] + '@snu.ac.kr'
            email = EmailMessage(mail_title, message, to=[mail_to])
            email.send()
            return render(request, 'accounts/login.html', {'error': 'Check email for validation'})

    return render(request, 'accounts/signup.html')



def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        exist = User.objects.filter(username=username).first()
        if not exist:
            return render(request, 'accounts/login.html', {'error' : 'User not found'})
        user = auth.authenticate(request, username=username, password=password)
        if user is not None and user.is_active==True:
            if user.pw_changing == True:
                return render(request, 'accounts/changepw.html')
            elif user.groups.filter(name='faculty').exists() or user.is_superuser:
                auth.login(request, user)
                return redirect('home')
            else: return render(request, 'accounts/login.html', {'error' : 'Please wait for Faculty approval'})
        elif user is not None and user.is_active()==False:
            return render(request, 'accounts/login.html', {'error' : 'Validate your account via email'})
        else:
            return render(request, 'accounts/login.html', {'error': 'Username or Password incorrect'})
    else:
        return render(request, 'accounts/login.html')

"""
def logout(request):
    # 포스트 방식으로 들어오면
    if request.method == 'POST':
        # 유저 로그아웃
        auth.logout(request)
        return redirect('home')
    return render(request, 'accounts/login.html')
"""


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExsit):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("login")
    else:
        return render(request, 'accounts/login.html', {'error' : '계정 활성화 오류'})
    return 
