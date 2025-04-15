from rest_framework.serializers import ValidationError
import re


def validate_password(value):
    password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    if not password_pattern.match(value):
        raise ValidationError(
            "Пароль должен содержать хотя бы одну заглавную букву, одну строчную букву, одну цифру "
            "и один специальный символ (@$!%*?&)."
        )
    return value
