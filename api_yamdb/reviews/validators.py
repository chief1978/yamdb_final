from django.utils import timezone
from rest_framework.serializers import ValidationError


def cur_year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            ('Год выпуска произведения, %(value)s, больше текщего года!'),
            params={'value': value},
        )
