from decimal import ROUND_HALF_UP, Decimal
from catalog.models.order import OrderItem
from payments.models.tax import Tax
from payments.models.discount import Discount

class PricingService:
    def __init__(self, order):
        self.order = order

    def set_discount(self, code):
        discount = Discount.objects.filter(code=code).first()
        if discount:
            self.order.discount = discount
            self.order.save()
            return True
        return False

    def set_taxes(self, tax_ids_list):
        taxes = Tax.objects.filter(id__in=tax_ids_list)
        self.order.taxes.set(taxes)

    def get_total_price(self):
        items = OrderItem.objects.filter(order=self.order)
        subtotal = sum(oi.price_at_purchase * oi.quantity for oi in items)

        order_taxes = self.order.taxes.all()
        total_tax_rate = sum(tax.rate for tax in order_taxes)

        taxes_amount = (subtotal * total_tax_rate) / 100
        total = subtotal + taxes_amount

        discounted = total

        discount = self.order.discount
        if discount.percent_off:
            reduction = total * discount.percent_off / 100
            discounted -= reduction
        elif discount.amount_off:
            discounted -= discount.amount_off

        return {
            "total": total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "discounted": discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        }
