from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('verify/', views.verify_token, name='verify-token'),
    path('refresh/', views.refresh_token, name='refresh-token'),
    path('me/', views.me, name='me'),
]
