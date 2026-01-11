import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from catalog.models.order import Order
from payments.services.pricing import PricingService

@require_POST
def apply_promo(request, order_id):
    print('test')
    try:
        data = json.loads(request.body)
        code = data.get('code')
        target_currency = data.get('currency', 'RUB').upper()
        
        order = Order.objects.get(id=order_id)
        service = PricingService(order)
        
        success = service.set_discount(code)
        
        if success:
            pricing_data = service.get_total_price(target_currency)
            return JsonResponse({
                'success': True,
                'total': float(pricing_data['total']),
                'discount_amount': float(pricing_data['discount_amount'])
            })
        else:
            return JsonResponse({'success': False, 'message': 'Промокод не найден'}, status=400)
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)