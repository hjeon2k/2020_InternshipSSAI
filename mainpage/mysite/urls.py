"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from core.views import *
from words.views import *

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),

    path('', DocumentCreate.as_view(), name='home'),
    path('media/<path:relative_path>', DocumentDownload.as_view(), name='document-download'),
    path('document-delete/<int:pk>', DocumentDelete, name='document-delete'),
    path('videoedit/<path:relative_path>', VideoEdit, name='videoedit'),
    path('audioedit/<path:relative_path>', AudioEdit, name='audioedit'),
    
    path('wordset/', WordsetCreate.as_view(), name='wordset'),
    path('wordset-delete/<int:pk>', WordsetDelete, name='wordset-delete'),

    path('userlist/', UserList.as_view(), name='userlist'),
    path('user-approve/<str:name>', UserApprove, name='user-approve'),
    path('user-delete/<str:name>', UserDelete, name='user-delete'),
]
