import stripe
from django.conf import settings
from payments.services.pricing import PricingService

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment_intent(order, currency):
    pricing = PricingService(order)
    prices = pricing.get_total_price()
    
    stripe_amount = int(prices["total"] * 100)
    
    return stripe.PaymentIntent.create(
        amount=stripe_amount,
        currency=currency.lower(),
        metadata={
            'order_id': order.id,
            'session_key': order.session_key
        }
    )
    