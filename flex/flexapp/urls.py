from django.urls import path
from . import views

urlpatterns = [

    path('',views.CustomLogin,name="login"),
    path('logout', views.CustomLogout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    # path('updateLeet/<int:count>',views.UpdateLeet, name="updateLeet"),
    path('register', views.register, name="register"),
    path('create-project', views.create_project, name="create_project"),
    path('add-certification', views.add_certification, name="add_certification"),  
]
