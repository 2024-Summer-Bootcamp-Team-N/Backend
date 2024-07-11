from django.urls import path
from . import views

urlpatterns = [
    path('login', views.LoginView.as_view(), name='users_login_create'),
    path('logout', views.LogoutView.as_view(), name='users_logout_delete'),
    path('signup', views.SignupView.as_view(), name='users_signup_create'),
]

