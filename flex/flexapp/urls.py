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
    path('faculty', views.faculty, name="faculty"),
    path('student/<str:rollno>', views.studentView, name="studentView"),
    path('edit_project', views.edit_project, name="edit_project"),
    path('delete_project/<int:primary_key>', views.delete_project,name="delete_project"),
    path('delete_certification/<int:primary_key>', views.delete_certification, name="delete_certification"),
    path('edit_certification', views.edit_certification, name="edit_certification"),
    path('leetcode/<str:leetcode_user>', views.leetcode_request, name="leetcode"),
    path('download', views.download_request, name="download"),
    path('verify_otp', views.verify_otp, name="verify_otp"),
    path('forgot_password/verify', views.verify_otp_forgot, name="verify_otp_forgot"),
    path('forgot_password', views.forgot_password, name="forgot_password"),
    path('reset_password', views.reset_password, name="reset_password"),
    path('profile/', views.student_profile, name='student_profile'),
]
