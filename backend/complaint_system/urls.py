from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/notifications/', include('notifications.urls')),
]
