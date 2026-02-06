from django.conf import settings
from django.db import models

class DiscountCode(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = 'percent', 'Percent'
        FIXED = 'fixed', 'Fixed'

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discount_codes')
    code = models.CharField(max_length=50)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    value = models.PositiveIntegerField()
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    max_uses = models.PositiveIntegerField(default=0)   # 0 یعنی نامحدود
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('seller', 'code')

    def __str__(self):
        return f"{self.code} ({self.seller})"
