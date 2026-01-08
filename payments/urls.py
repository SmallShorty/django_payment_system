from django.urls import path

from payments import views


urlpatterns = [
    path("stripe/checkout/<int:order_id>/", views.checkout, name="checkout"),
    path(
        "stripe/create-payment-intent/<int:order_id>/",
        views.payment_intent_view,
        name="create_payment_intent",
    ),
    path('payment-complete/', views.payment_complete, name='payment_complete'),
]
