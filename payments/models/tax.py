from django.db import models

class Tax(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    stripe_tax_rate_id = models.CharField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"