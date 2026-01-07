from django.db import models

class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    amount_off = models.PositiveIntegerField(null=True, blank=True, help_text="Fixed amount discount")
    percent_off = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stripe_coupon_id = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.code