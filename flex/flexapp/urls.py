from django.urls import path
from . import views

urlpatterns = [

    path('',views.CustomLogin,name="login"),
    path('logout', views.logout_view, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
]