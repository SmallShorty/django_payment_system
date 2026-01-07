from django.db import models
from config.constants import Currency


class Item(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.PositiveIntegerField(
        verbose_name="Цена",
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.RUB,
        verbose_name="Валюта"
    )

    def __str__(self):
        return f"{self.name} ({self.price} {self.currency})"
