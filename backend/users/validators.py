import re

from django.core.exceptions import ValidationError

from api_foodgram.constans import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH


def validate_username(username):

    pattern = r'^[\w.@+-]+\Z'

    if len(username) > NAME_MAX_LENGTH:
        raise ValidationError(
            f'Длина username больше допустимого - {NAME_MAX_LENGTH}!'
        )

    if not re.match(pattern, username):
        forbidden_characters = re.findall(pattern, username)
        raise ValidationError(f'Логин содержит недопустимые символы: '
                              f'{forbidden_characters}')
    return username


def validate_email(email):
    if len(email) > EMAIL_MAX_LENGTH:
        raise ValidationError(
            f'Длина email больше допустимого - {EMAIL_MAX_LENGTH}!'
        )
    return email
