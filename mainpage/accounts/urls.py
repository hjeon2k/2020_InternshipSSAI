from django.urls import path
from . import views

from django.contrib.auth import views as auth_views
   
urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('findchangepw/', views.findchangepw, name="findchangepw"),
    path('changepw/', views.changepw, name="changepw"),
    path('login/', views.login, name="login"),
    path('logout/',auth_views.LogoutView.as_view(), name='logout' ),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name="activate"),
]
