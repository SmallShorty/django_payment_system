from django.db import models

class Order(models.Model):
    session_key = models.CharField(max_length=40, db_index=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    items = models.ManyToManyField('Item', through='OrderItem')
    
    taxes = models.ManyToManyField('payments.Tax', blank=True)
    discount = models.ForeignKey('payments.Discount', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_paid = models.BooleanField(default=False)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.PositiveIntegerField()