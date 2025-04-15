from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.utils import timezone


class InvalidateOldTokenSerializerMixin:

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = SlidingToken.for_user(self.user)

        decoded_token = refresh.payload
        new_jti = decoded_token['jti']

        old_tokens = OutstandingToken.objects.filter(
            user=self.user,
            expires_at__gt=timezone.now(),
        ).exclude(jti=new_jti)

        for token in old_tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        data['token'] = str(refresh)
        return data
