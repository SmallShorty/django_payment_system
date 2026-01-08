from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe

from catalog.models.order import Order
from payments.services.pricing import PricingService
from payments.services.stripe import create_stripe_payment_intent

@csrf_exempt
def payment_intent_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    currency = request.GET.get('currency', 'usd').lower()
    
    try:
        intent = create_stripe_payment_intent(order, currency)
        
        return JsonResponse({
            'clientSecret': intent.client_secret,
            'amount': intent.amount
        })

    except stripe.error.StripeError as e:
        print(f"[Stripe API Error]: Order #{order.id} - {str(e)}")
        return JsonResponse({'error': 'Ошибка платежной системы'}, status=400)
        
    except Exception as e:
        print(f"[System Error]: Failed for Order #{order.id}. Details: {str(e)}")
        return JsonResponse({'error': 'Произошла внутренняя ошибка'}, status=500)
 
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    currency = request.GET.get('currency', 'rub').lower()
    
    pricing = PricingService(order)
    prices = pricing.get_total_price()

    return render(request, 'payments/stripe/checkout.html', {
        'order': order,
        'total_price': prices.get("discounted", prices.get("total")),
        'currency': currency,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    })
    
def payment_complete(request):
    context = {
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
        
        'provider': request.GET.get('provider'),
        'order_id': request.GET.get('order_id'),
    }
    
    return render(request, 'payments/payment_complete.html', context)