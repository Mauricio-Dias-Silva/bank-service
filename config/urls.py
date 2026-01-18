from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fintech/', include('fintech.urls')),
    path('', lambda r: __import__('django.shortcuts').shortcuts.redirect('fintech/app/')), # Auto-redirect root
]
