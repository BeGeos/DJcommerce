from django.urls import path
from .views import StoreView, ProductDetailView, add_to_cart
from .views import remove_from_cart, register, OrderSummaryView, CheckoutView, order_summary_view
from .views import add_single_product, remove_single_product, update_address, PaymentView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', StoreView.as_view(), name='homepage'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/<int:pk>', add_to_cart, name='add-to-cart'),
    path('add-one-to-cart/<int:pk>', add_single_product, name='add-one-to-cart'),
    path('remove-from-cart/<int:pk>', remove_from_cart, name='remove-from-cart'),
    path('remove-one-from-cart/<int:pk>', remove_single_product, name='remove-one-from-cart'),
    path('user/register', register, name='sign-up'),
    path('cart/', OrderSummaryView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/payment/<payment_options>', PaymentView.as_view(), name='payment'),
    path('checkout/summary/<pk>', order_summary_view, name='order-summary'),
    path('update/address', update_address, name='new-address')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
