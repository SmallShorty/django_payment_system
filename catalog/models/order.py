from django.db import models

from config.constants import Currency

class Order(models.Model):
    session_key = models.CharField(max_length=40, db_index=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    items = models.ManyToManyField('Item', through='OrderItem')
    
    taxes = models.ManyToManyField('payments.Tax', blank=True)
    discount = models.ForeignKey('payments.Discount', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_paid = models.BooleanField(default=False)
    
    @property
    def total_items(self):
        return self.orderitem_set.count()

    def add_or_update_item(self, item, quantity):
        order_item, created = OrderItem.objects.get_or_create(
            order=self,
            item=item,
            defaults={"price_at_purchase": item.price},
        )
        if not created:
            order_item.quantity += int(quantity)
        else:
            order_item.quantity = int(quantity)
        
        if order_item.quantity <= 0:
            order_item.delete()
        else:
            order_item.save()
        return order_item

    def get_currencies(self):
        return list(self.orderitem_set.values_list('item__currency', flat=True).distinct())

    def set_paid(self):
        self.is_paid = True
        self.save()
        


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
    )
