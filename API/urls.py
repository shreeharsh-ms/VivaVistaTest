# API/urls.py
from django.urls import path
from . import views  # Import the views from the API app
from .views import schedule_viva
from .views import upload_pdf
from .views import STDlogin
from .views import STDconf
from .views import STDpass
from .views import STDashboard

urlpatterns = [
    path('', views.Landing_page, name='Landing_page'),
    path('host_dashboard/', views.home, name='host_dashboard'),
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('schedule_viva/', views.schedule_viva, name='schedule_viva'),
    # path('api/questions/', views.get_questions, name='get_questions'),
    path('std_login/', views.STDlogin, name='STDlogin'),
    path('host_login/', views.HOSTlogin, name='HOSTlogin'),
    path('std_conf/', views.STDconf, name='STDconf'),
    path('std_pass/', views.STDpass, name='STDpass'),
    path('std_dashboard/', views.STDashboard, name='STDashboard'),
    path('questions/', views.questions, name='questions'),
    path('download_csv/<str:user_id>/<str:subject_name>/', views.download_csv, name='download_csv'),
    path('start_session/', views.start_session, name='start_session'),
    path('process-transcript/', views.process_transcript, name='process_transcript'),
    path('end_session/', views.end_session, name='end_session'),
    path('generate_otp/', views.generate_otp, name='generate_otp'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('generate_classroom_id/', views.generate_classroom_id, name='generate_classroom_id'),
    path('process_frame/', views.process_frame, name='process_frame'),
    path('facProfile/', views.STDprofile, name='STDprofile'),
    path('STDanalytics/', views.STDanalytics, name='STDanalytics'),
    path('Notifications/', views.Notifications, name='Notifications'),
    path('CreateClassroom/', views.CreateClassroom, name='CreateClassroom'),
    path('store-classroom-code/', views.store_classroom_code, name='store_classroom_code'),
    path('accounts/login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('hosts_login/', views.hosts_login, name='hosts_login'),
    path('join_classroom/', views.join_classroom, name='join_classroom'),
    path('store_transcripts_to_mongo/', views.store_transcripts_to_mongo, name='store_transcripts_to_mongo'),
    path('FinalScore/', views.FinalScore, name='FinalScore'),
    path('Store_questions/', views.store_json_in_mongodb, name='Store_questions'),
    path('Viva_selection/', views.Viva_selection, name='Viva_selection'),
    path('signUp/', views.StdHost, name='StdHost'),
    path('StdSignIN/', views.StdSignIN, name='StdSignIN'),
 

]

#########################################################################################################################



