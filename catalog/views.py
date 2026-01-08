from django.shortcuts import get_object_or_404, redirect, render
from catalog.models.item import Item
from catalog.services.order import OrderService

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'catalog/item_detail.html', {'item': item})

def add_to_cart(request, item_id):
    if request.method == 'POST':
        order_service = OrderService(request)
        order_service.add_item(item_id=item_id, quantity=1)
    
    return redirect('item_detail', pk=item_id)