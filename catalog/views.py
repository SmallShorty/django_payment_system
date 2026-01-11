from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from catalog.models.item import Item
from catalog.models.order import Order
from catalog.services.order import OrderService
from payments.services.pricing import PricingService


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, "catalog/item_detail.html", {"item": item})


def add_to_cart(request, item_id):
    if request.method == "POST":
        order_service = OrderService(request)
        order_service.add_item(item_id=item_id, quantity=1)

    return redirect("item_detail", pk=item_id)


def cart_detail(request):
    order_service = OrderService(request)
    order = order_service.order
    
    pricing_service = PricingService(order)
    pricing_data = pricing_service.get_total_price(target_currency="RUB")
    
    return render(
        request,
        "catalog/cart_detail.html",
        {
            "order": order,
            "total_cost": pricing_data["total"],          
            "discount_amount": pricing_data["discount_amount"], 
            "subtotal": pricing_data["subtotal"],        
        },
    )


def cart_update(request, item_id, action):
    order_service = OrderService(request)
    order = order_service.order

    if action == "add":
        order_service.add_item(item_id, quantity=1)
    elif action == "reduce":
        oi = order.orderitem_set.filter(item_id=item_id).first()
        if oi:
            order_service.update_quantity(item_id, oi.quantity - 1)

    order_item = order.orderitem_set.filter(item_id=item_id).first()
    
    pricing_service = PricingService(order)
    pricing_data = pricing_service.get_total_price()
    

    return JsonResponse(
        {
            "success": True,
            "item_qty": order_item.quantity if order_item else 0,
            "total_qty": order_service.get_items_count(),
            "total_cost": str(pricing_data["total"]),
        }
    )


def cart_clear(request):
    order_service = OrderService(request)
    order_service.clear_order()
    return redirect("cart_detail")


def shop_view(request):
    items = Item.objects.all()
    return render(request, 'catalog/product_list.html', {'items': items})

def get_cart_total(request, order_id, currency):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        target_currency = currency.upper()
        order = get_object_or_404(Order, id=order_id)
        
        service = PricingService(order)
        pricing_data = service.get_total_price(target_currency=target_currency) 
        
        final_total = pricing_data.get('total', 0)
        
        return JsonResponse({
            'success': True,
            'total_cost': f"{final_total:.2f}",
            'currency': target_currency
        })
    
    return JsonResponse({'success': False}, status=400)