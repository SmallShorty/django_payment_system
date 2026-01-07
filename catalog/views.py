from django.shortcuts import get_object_or_404, render
from catalog.models.item import Item

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'catalog/item_detail.html', {'item': item})