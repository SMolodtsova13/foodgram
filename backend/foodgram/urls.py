from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from api.views import redirect_to_full_recipe

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('<str:short_url>', redirect_to_full_recipe),
] + static(.STATIC_URL, document_root=settings.STATIC_ROOT)
