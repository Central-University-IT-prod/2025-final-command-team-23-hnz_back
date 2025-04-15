from django.conf import settings
from django_minio_backend import MinioBackend

import logging


class LoyalTMinioBackend(MinioBackend):
    def url(self, name):
        original_url = super().url(name)
        return original_url.replace(settings.MINIO_URL, settings.MINIO_REDIRECT_URL)
