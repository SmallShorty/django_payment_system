from catalog.services.order import OrderService

def cart_info(request):
    service = OrderService(request)
    return {
        'cart_total_quantity': service.get_items_count()
    }