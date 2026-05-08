from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report, name='report'),
    path('submit/', views.submit_report, name='submit_report'),
    path('track/<str:citizen_token>/', views.track_report, name='track_report'),
    path('r/<str:dept_token>/', views.department_report, name='department_report'),
    path('r/<str:dept_token>/update/', views.update_status, name='update_status'),
    path('api/classify-photo/', views.classify_photo, name='api_classify_photo'),
    path('test-email/', views.test_email_view, name='test_email'),
]
