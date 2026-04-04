from django.urls import path
from . import views

urlpatterns = [
    # Registration (forwarded to centralized auth)
    path('register/', views.register, name='indie-register'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]
