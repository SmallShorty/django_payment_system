from django.contrib import admin
from catalog.models.order import Order, OrderItem
from payments.models.tax import Tax
from payments.models.discount import Discount

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 
    fields = ('item', 'quantity',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_key', 'is_paid', 'created_at', 'discount')
    list_filter = ('is_paid', 'created_at', 'taxes')
    search_fields = ('session_key', 'id')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('session_key', 'is_paid')
        }),
        ('Налоги и Скидки', {
            'fields': ('discount', 'taxes')
        }),
    )

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'stripe_tax_rate_id')

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'stripe_coupon_id')