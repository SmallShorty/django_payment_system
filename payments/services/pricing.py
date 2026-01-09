from decimal import ROUND_HALF_UP, Decimal

import requests
from catalog.models.order import OrderItem
from payments.models.tax import Tax
from payments.models.discount import Discount

class PricingService:
    def __init__(self, order):
        self.order = order

    @classmethod
    def convert(cls, amount: float, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return amount

        params = {
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper()
        }

        try:
            response = requests.get(cls.API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            return data['rates'][to_currency.upper()]
        
        except requests.RequestException as e:
            raise ValueError(f"Ошибка при запросе к API: {e}")
        except KeyError:
            raise ValueError(f"Валюта {to_currency} не найдена.")

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
        subtotal = sum((oi.price_at_purchase * oi.quantity for oi in items), Decimal("0.00"))

        discount_value = Decimal("0.00")
        discount = self.order.discount
        
        if discount:
            if discount.percent_off:
                discount_value = (subtotal * discount.percent_off) / Decimal("100")
            elif discount.amount_off:
                discount_value = discount.amount_off
        
        discounted_subtotal = max(subtotal - discount_value, Decimal("0.00"))

        order_taxes = self.order.taxes.all()
        total_tax_rate = sum((tax.rate for tax in order_taxes), Decimal("0.00"))
        taxes_amount = (discounted_subtotal * total_tax_rate) / Decimal("100")

        final_total = discounted_subtotal + taxes_amount

        return {
            "subtotal": subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "discount_amount": discount_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "tax_amount": taxes_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "total": final_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        }
