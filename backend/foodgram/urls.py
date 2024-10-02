from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('s/', include('recipes.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
