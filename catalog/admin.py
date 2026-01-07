from django.contrib import admin
from catalog.models.item import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "currency")
    list_filter = ("currency",)
    search_fields = ("name", "description")
