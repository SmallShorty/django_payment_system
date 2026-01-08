from catalog.models.order import Order, OrderItem
from catalog.models import Item

class OrderService:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.order = self._get_or_init_order()

    def _get_or_init_order(self):
        if not self.session.session_key:
            self.session.create()

        session_key = self.session.session_key
        order_id = self.session.get("order_id")

        order = (
            Order.objects.filter(id=order_id, is_paid=False).first()
            if order_id
            else None
        )

        if not order:
            order = Order.objects.filter(session_key=session_key, is_paid=False).first()

        if not order:
            order = Order.objects.create(session_key=session_key)
            self.session["order_id"] = order.id
            self.session.modified = True

        return order

    def add_item(self, item_id, quantity=1):
        item = Item.objects.get(id=item_id)
        order_item, created = OrderItem.objects.get_or_create(
            order=self.order,
            item=item,
            defaults={"price_at_purchase": item.price},
        )
        if not created:
            order_item.quantity += int(quantity)
            order_item.save()
        return order_item

    def update_quantity(self, item_id, quantity):
        quantity = int(quantity)
        if quantity <= 0:
            OrderItem.objects.filter(order=self.order, item_id=item_id).delete()
            return

        order_item = OrderItem.objects.filter(order=self.order, item_id=item_id).first()
        if order_item:
            order_item.quantity = quantity
            order_item.save()
        else:
            self.add_item(item_id, quantity=quantity)

    def clear_order(self):
        if "order_id" in self.session:
            del self.session["order_id"]
            self.session.modified = True
            
    def get_items_count(self):
        return OrderItem.objects.filter(order=self.order).count()
    
    def mark_as_paid(self):
        if not self.order.is_paid:
            self.order.is_paid = True
            
            self.order.save()
            
            self.clear_order()
            return True
        return False