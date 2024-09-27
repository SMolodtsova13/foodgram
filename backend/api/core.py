import base64
# from sqids import Sqids

# from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator

# from users.validators import validate_username, validate_email
# from users.models import Follow
# from recipes.models import (Tag, Favourites, Ingredient, Recipe,
#                             IngredientRecipe, ShoppingList, TagRecipe)


class Base64ImageFieldSerializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)
