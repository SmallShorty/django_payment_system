from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from catalog.models.item import Item
from catalog.services.order import OrderService


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
    return render(
        request,
        "catalog/cart_detail.html",
        {
            "order": order_service.order,
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
    return JsonResponse(
        {
            "success": True,
            "item_qty": order_item.quantity if order_item else 0,
            "total_qty": order_service.get_total_quantity(),
            "total_cost": order.get_total_cost(),
        }
    )


def cart_clear(request):
    order_service = OrderService(request)
    order_service.clear_order()
    return redirect("cart_detail")


def shop_view(request):
    # Получаем все товары из базы данных
    items = Item.objects.all()
    
    # Рендерим шаблон shop.html и передаем туда товары
    return render(request, 'catalog/shop.html', {'items': items})