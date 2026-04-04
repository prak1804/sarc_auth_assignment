from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Home route 
def home(request):
    return JsonResponse({
        "message": "SARC Auth Service is running 🚀",
        "status": "ok"
    })


urlpatterns = [
    path('admin/', admin.site.urls),

    # Root endpoint
    path('', home),


    # Auth APIs
    path('api/auth/', include('auth_app.urls')),
]