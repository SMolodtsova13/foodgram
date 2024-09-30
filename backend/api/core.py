import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from rest_framework import serializers

from recipes.models import Recipe


class Base64ImageFieldSerializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


def redirect_to_full_recipe(request, short_url):
    recipe = get_object_or_404(Recipe, short_url=short_url)
    full_url = f'/recipes/{recipe.id}'
    return HttpResponseRedirect(full_url)
