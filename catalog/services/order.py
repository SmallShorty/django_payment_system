from catalog.models.order import Order, OrderItem
from catalog.models import Item
from payments.services.pricing import PricingService

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
            
        pricing = PricingService(order)
        pricing.set_taxes()

        return order

    def add_item(self, item_id, quantity=1):
        item = Item.objects.get(id=item_id)
        return self.order.add_or_update_item(item, quantity)

    def mark_as_paid(self):
        if not self.order.is_paid:
            self.order.set_paid()
            self.clear_order()
            return True
        return False

    def clear_order(self):
        self.session.pop("order_id", None)
        self.session.modified = True
    
    def get_items_count(self):
        return self.order.total_items