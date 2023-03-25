import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if re.search(r'^[\w.@+-]+$', value) is None:
        raise ValidationError(('Username has unallowed symbols'),)
    if value == 'me':
        raise ValidationError(('You cant use me as username'),)
