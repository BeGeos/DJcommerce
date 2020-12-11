from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from .models import *
from .forms import UserRegisterForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, UpdateAddressForm
from django.contrib.auth.decorators import login_required


class StoreView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'product_list'


class OrderSummaryView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(customer=self.request.user, complete=False)
            context = {
                'object': order
            }
            return render(self.request, 'order-summary.html', context)
        except ObjectDoesNotExist:
            # messages.info(self.request, 'Your cart is empty')
            return render(self.request, 'order-summary.html')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get_queryset(self):
        self.product = get_object_or_404(Product, id=self.kwargs['pk'])
        return Product.objects.filter(id=self.product.id)

    def get_context_data(self, **kwargs):
        suggest = []
        context = super().get_context_data(**kwargs)
        suggestions = Product.objects.filter(category__contains=self.product.category)
        for each in suggestions:
            if each.id != self.product.id:
                suggest.append(each)
        suggestions = suggest[:3]
        context['suggestions'] = suggestions
        return context


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # print('is Valid')
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        # print('is not Valid')
        form = UserRegisterForm()
    return render(request, 'sign_up.html', {'form': form})


def add_to_cart(request, pk):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=pk)
        order_item, created = OrderItem.objects.get_or_create(product=product, customer=request.user)
        order_qs = Order.objects.filter(customer=request.user, complete=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.products.filter(product__id=product.id).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, 'Quantity updated')
            else:
                order.products.add(order_item.id)
                messages.info(request, f'{product} was added to your cart')
        else:
            # order_date = timezone.now()
            order = Order.objects.create(customer=request.user)
            order.products.add(order_item.id)
            messages.info(request, f'{product} was added to your cart')
        return redirect('product-detail', pk=pk)
    else:
        return redirect('login')


def remove_from_cart(request, pk):
    product = get_object_or_404(Product, id=pk)
    order_qs = Order.objects.filter(customer=request.user, complete=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__id=product.id).exists():
            order_item = OrderItem.objects.get(product=product, customer=request.user)
            order.products.remove(order_item.id)
            order_item.delete()
            messages.info(request, f'{product} was removed from your cart')
    return redirect('cart')


def add_single_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    order_item = OrderItem.objects.get(product=product, customer=request.user)
    order_qs = Order.objects.filter(customer=request.user, complete=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__id=product.id).exists():
            order_item.quantity += 1
            order_item.save()
    return redirect('cart')


def remove_single_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    order_qs = Order.objects.filter(customer=request.user, complete=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__id=product.id).exists():
            order_item = OrderItem.objects.get(product=product, customer=request.user)
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.products.remove(order_item)
    return redirect('cart')


def get_shipping_address(request, cleaned_data):
    address_qs = ShippingAddress.objects.filter(customer=request.user,
                                                saved=False)
    if address_qs.exists():
        address_qs.delete()

    # order = Order.objects.get(customer=request.user)
    address = ShippingAddress.objects.create(
            customer=request.user,
            saved=cleaned_data.get('save_address'),
            address=cleaned_data.get('address'),
            city=cleaned_data.get('city'),
            state=cleaned_data.get('state'),
            zipcode=cleaned_data.get('zipcode'),
            country=cleaned_data.get('country')
        )
    address.save()
    return address


def get_payment_info(request, cleaned_data):
    payment_qs = PaymentInformation.objects.filter(customer=request.user,
                                                   saved=False)
    if payment_qs.exists():
        payment_qs.delete()

    payment_info = PaymentInformation.objects.create(customer=request.user,
                                                     saved=cleaned_data.get('save_payment_information'),
                                                     name_on_card=cleaned_data.get('Name_on_Card'),
                                                     card_number=cleaned_data.get('Card_Number'),
                                                     expiration_date=cleaned_data.get('Expiration'),
                                                     CVV=cleaned_data.get('CVV'))
    payment_info.save()


class CheckoutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        address_qs = ShippingAddress.objects.filter(customer=self.request.user,
                                                    saved=True)
        if address_qs.exists():
            saved_option = True
        else:
            saved_option = False
        context = {
            'form': form,
            'saved': saved_option
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        # print(form.get('use_default_address'))
        try:
            order = Order.objects.get(customer=self.request.user, complete=False)
            if form.is_valid():
                # print('the form is valid')
                address = get_shipping_address(self.request, form.cleaned_data)
                order.shipping_address = address
                order.save()
                # print(form.cleaned_data)
            return redirect('payment', payment_options=form.cleaned_data.get('payment_options'))
        except ObjectDoesNotExist:
            messages.info(self.request, 'Your cart is empty')
            return redirect('cart')
        # address_qs = ShippingAddress.objects.filter(customer=self.request.user)
        # if address_qs.exists():
        #     return redirect('new-address')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(customer=self.request.user,
                                  complete=False)
        products = order.products.all()
        context = {
            'products': products,
            'order': order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(customer=self.request.user,
                                      complete=False)
            order.complete = True
            # order_items = order.products.all()
            # for each in order_items:
            #     each.delete()
            order.save()
            return redirect('order-summary', pk=order.id)
        except ObjectDoesNotExist:
            messages.info(self.request, 'You cart is empty')
            return redirect('cart')


# part of the user profile
def update_address(request):
    if request.method == 'POST':
        form = UpdateAddressForm(request.POST)
        if form.is_valid():
            old_address = ShippingAddress.objects.get(customer=request.user)
            old_address.delete()
            get_shipping_address(request, form.cleaned_data)
            # print(form.cleaned_data)
            messages.info(request, 'Your address was updated successfully')
            return redirect('checkout')
    else:
        form = UpdateAddressForm()
    context = {
        'form': form
    }
    return render(request, 'new_address.html', context)


def order_summary_view(request, pk):
    order_display = Order.objects.get(id=pk)
    context = {
        'order': order_display
    }
    return render(request, 'summary.html', context)
