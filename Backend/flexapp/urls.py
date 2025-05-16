from django.urls import path
from . import views
from .views import upload_students, search_students

urlpatterns = [

    path('',views.CustomLogin,name="login"),
    path('logout', views.CustomLogout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    # path('updateLeet/<int:count>',views.UpdateLeet, name="updateLeet"),
    # path('register', views.register, name="register"),
    path('create-project', views.create_project, name="create_project"),
    path('add-certification', views.add_certification, name="add_certification"), 
    path('faculty', views.faculty, name="faculty"),
    path('coordinator/dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
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
    path('profile', views.student_profile, name='profile'),
    path('upload_students/', upload_students, name='upload_students'),
    path("search_students/", search_students, name="search_students"),
    path("search_technologies/", views.search_technologies, name="search_technologies"),
    path('dashboard/placement/', views.placement_dashboard, name='placement_dashboard'),
    path("create/", views.create_form, name="create_form"),
    path("assigned/", views.list_assigned_forms, name="list_assigned_forms"),
    path("fill/<int:form_id>/", views.get_form, name="fill_form_detail"),
    path('forms/', views.form_list_view, name='form_list'),
    path('forms/<int:form_id>/', views.form_detail_view, name='form_detail'),
    path('forms/<int:form_id>/download/<str:download_type>/', views.download_csv, name='download_csv'),
    
    # API Endpoints
    path('api/', views.api_overview, name='api-overview'),
    path('api/students/', views.student_list, name='api-students'),
    path('api/student/<str:rollno>/', views.student_detail, name='api-student-detail'),
    path('api/technologies/', views.technology_list, name='api-technologies'),
    path('api/projects/', views.project_list, name='api-projects'),
    path('api/projects/create/', views.create_project_api, name='api-create-project'),
    path('api/certificates/', views.certificate_list, name='api-certificates'),
    path('api/certificates/create/', views.create_certificate_api, name='api-create-certificate'),
    
    # API Auth Endpoints
    path('api/login/', views.api_login, name='api-login'),
    path('api/logout/', views.api_logout, name='api-logout'),
    path('api/current-user/', views.api_current_user, name='api-current-user'),
]
