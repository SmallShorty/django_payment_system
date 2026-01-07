from django.db import models

class Currency(models.TextChoices):
    RUB = "rub", "RUB"
    USD = "usd", "USD"
    EUR = "eur", "EUR"