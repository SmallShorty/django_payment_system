from decimal import ROUND_HALF_UP, Decimal

import requests
from catalog.models.order import OrderItem
from payments.models.tax import Tax
from payments.models.discount import Discount

class PricingService:
    def __init__(self, order):
        self.order = order

    @classmethod
    def convert(cls, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency == to_currency:
            return Decimal(str(amount))

        rates = cls.get_rates_batch(from_currency, [to_currency])
        if to_currency not in rates:
            raise ValueError(f"Курс для {to_currency} не найден.")
            
        return (Decimal(str(amount)) * rates[to_currency]).quantize(Decimal("0.000001"))
    
    @classmethod
    def get_rates_batch(cls, base_currency: str, target_currencies: list) -> dict:
        base_currency = base_currency.upper()
        targets = {c.upper() for c in target_currencies if c.upper() != base_currency}
        if not targets:
                return {}
        params = {
            "from": base_currency,
            "to": ",".join(targets)
        }
        try:
            response = requests.get(cls.API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return {curr: Decimal(str(rate)) for curr, rate in data.get('rates', {}).items()}
        except requests.RequestException as e:
            raise ValueError(f"API convertion error: {e}")
        
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

    def get_total_price(self, target_currency="RUB"):
        target_currency = target_currency.upper()
        order_items = OrderItem.objects.filter(order=self.order).select_related('item')
        
        item_currencies = {oi.item.currency for oi in order_items}
        rates = self.get_rates_batch(target_currency, list(item_currencies))
        
        subtotal = Decimal("0.00")
        
        for oi in order_items:
            item_curr = oi.item.currency.upper()
            price = Decimal(str(oi.item.price))
            
            if item_curr == target_currency:
                item_price_in_order_curr = price
            else:
                rate = rates.get(item_curr)
                item_price_in_order_curr = price / rate
                    
            subtotal += item_price_in_order_curr * oi.quantity

        discount_value = Decimal("0.00")
        discount = self.order.discount
        
        if discount:
            if discount.percent_off:
                discount_value = (subtotal * discount.percent_off) / Decimal("100")
            elif discount.amount_off:
                discount_value = self.convert(
                    amount=discount.amount_off,
                    from_currency=discount.currency,
                    to_currency=self.order.currency
                )
        
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
