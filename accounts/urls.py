from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name ='accounts'

urlpatterns =[
    path('',views.Login,name='login'),
    path("logout",views.Logout,name="logout"),
    path('register',views.AccountRegistration.as_view(), name='register'),
    path("home",views.home,name="home"),
    path("guest_login",views.guest_login,name="guest_login"),
]