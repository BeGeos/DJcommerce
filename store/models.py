from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import redirect, reverse

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    description = models.TextField(default='Insert description here')
    category = models.CharField(max_length=32, blank=True, null=True)
    digital = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={
            'pk': self.id
        })

    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', kwargs={
            'pk': self.id
        })


class OrderItem(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

    def get_total_price(self):
        return self.quantity * self.product.price


class ShippingAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=50, null=False)
    date_added = models.DateTimeField(auto_now_add=True)
    saved = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.address


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    products = models.ManyToManyField(OrderItem)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True)
    transaction_id = models.CharField(max_length=200, null=True, default=100)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.transaction_id)

    def get_final_price(self):
        total = 0
        for order_item in self.products.all():
            total += order_item.get_total_price()
        return total


class ProductPictures(models.Model):
    image = models.ImageField(upload_to='product_pic', blank=True, null=True)
    # carousel = models.ImageField()
    product = models.OneToOneField(Product, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.product.name} pic'


class PaymentInformation(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    name_on_card = models.CharField(max_length=100)
    card_number = models.IntegerField()
    expiration_date = models.DateField()
    CVV = models.IntegerField()
    saved = models.BooleanField(default=False)

    def __str__(self):
        return self.customer.username
