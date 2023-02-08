from django.urls import path
from . import views

app_name ='accounts'

urlpatterns =[
    path('',views.Login,name='login'),
    path("logout",views.Logout,name="logout"),
    path('register',views.AccountRegistration.as_view(), name='register'),
    path("home",views.home,name="home"),
]