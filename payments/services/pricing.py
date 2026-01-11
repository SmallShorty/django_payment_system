from decimal import ROUND_HALF_UP, Decimal
from django.core.cache import cache
import requests
from venv import logger
from catalog.models.order import OrderItem
from config import settings
from payments.models.tax import Tax
from payments.models.discount import Discount

class PricingService:
    EXCHANGE_RATE_API_KEY = settings.EXCHANGE_RATE_API_KEY
    EXCHANGE_RATE_API_URL = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/"
    CACHE_TIMEOUT = 86400

    def __init__(self, order):
        self.order = order

    @classmethod
    def get_rates_batch(cls, base_currency: str, target_currencies: list) -> dict:
        base_currency = base_currency.upper()
        cache_key = f"rates_base_{base_currency}"
        
        rates_source = cache.get(cache_key)
        
        if not rates_source:
            url = f"{cls.EXCHANGE_RATE_API_URL}{base_currency}"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                if data.get('result') == 'success':
                    rates_source = data.get('conversion_rates', {})
                    cache.set(cache_key, rates_source, cls.CACHE_TIMEOUT)
                else:
                    return {}
            except Exception:
                return {}

        return {
            curr.upper(): Decimal(str(rates_source[curr.upper()])) 
            for curr in target_currencies 
            if curr.upper() in rates_source
        }

    def get_total_price(self, target_currency="RUB"):
        target_currency = target_currency.upper()
        order_items = OrderItem.objects.filter(order=self.order).select_related("item")
        
        currencies_to_fetch = {oi.item.currency.upper() for oi in order_items}
        discount = self.order.discount
        if discount and discount.amount_off and discount.currency:
            currencies_to_fetch.add(discount.currency.upper())

        rates = self.get_rates_batch(target_currency, list(currencies_to_fetch))

        subtotal = Decimal("0.00")
        for oi in order_items:
            item_curr = oi.item.currency.upper()
            price = Decimal(str(oi.item.price))
            
            if item_curr == target_currency:
                item_price_in_target = price
            else:
                rate = rates.get(item_curr)
                item_price_in_target = price / rate if rate else Decimal("0.00")

            subtotal += item_price_in_target * oi.quantity

        discount_value = Decimal("0.00")
        if discount:
            if discount.percent_off:
                discount_value = (subtotal * Decimal(str(discount.percent_off))) / Decimal("100")
            elif discount.amount_off:
                d_curr = discount.currency.upper()
                d_rate = rates.get(d_curr) if d_curr != target_currency else Decimal("1")
                discount_value = Decimal(str(discount.amount_off)) / d_rate if d_rate else Decimal("0.00")

        discounted_subtotal = max(subtotal - discount_value, Decimal("0.00"))
        
        order_taxes = self.order.taxes.all()
        total_tax_rate = sum((Decimal(str(tax.rate)) for tax in order_taxes), Decimal("0.00"))
        taxes_amount = (discounted_subtotal * total_tax_rate) / Decimal("100")
        
        final_total = discounted_subtotal + taxes_amount

        return {
            "subtotal": subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "discount_amount": discount_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "tax_amount": taxes_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "total": final_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        }

    def set_discount(self, code):
        discount = Discount.objects.filter(code=code).first()
        if discount:
            self.order.discount = discount
            self.order.save()
            return True
        return False

    def set_taxes(self, tax_ids_list=[]):
        """
        Устанавливает налоги для заказа. 
        
        Здесь может быть реализована различная логика в зависимости от заказа:
        - Проверка региона пользователя (tax nexus).
        - Применение налогов в зависимости от категории товаров (например, электроника vs продукты).
        - Налоги на основе общей суммы или типа плательщика (B2B/B2C).
        """
        vat_tax = Tax.objects.filter(name__icontains="VAT").first()
        if vat_tax:
            tax_ids_list.append(vat_tax.id)
                
        taxes = Tax.objects.filter(id__in=tax_ids_list)
        self.order.taxes.set(taxes)