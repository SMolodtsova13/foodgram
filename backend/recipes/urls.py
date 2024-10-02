from django.urls import path

from recipes.views import redirect_to_full_recipe

urlpatterns = [
    path('<str:short_url>', redirect_to_full_recipe),
]
