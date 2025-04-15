import enum
import uuid
from loyalT.minio import LoyalTMinioBackend
from django.db import models

from companies.models import Company


def item_image_upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)


class Item(models.Model):
    STATUS_CHOICES = (
        ("ACTIVE", "active"),
        ("INACTIVE", "inactive"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="items", on_delete=models.CASCADE)
    image = models.ImageField(
        storage=LoyalTMinioBackend(bucket_name='hnz-company-items'),
        upload_to=item_image_upload_to,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="ACTIVE")
    description = models.TextField(null=True, blank=True)

class StatusEnum(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
