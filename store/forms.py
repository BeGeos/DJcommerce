from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CheckoutForm(forms.Form):
    PAYMENT_OPTION = (
        ('S', 'Stripe'),
        ('P', 'PayPal'),
        ('CC', 'Credit Card')
    )

    # TODO use_default_address = forms.BooleanField(required=False)

    address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_or_suite = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment',
        'class': 'form-control'
    }))

    city = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'City',
        'class': 'form-control'
    }))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'custom-select d-block w-100'
    }))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    country = CountryField(blank_label='Select a country...').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        })
    )
    save_address = forms.BooleanField(required=False)

    payment_options = forms.ChoiceField(widget=forms.RadioSelect,
                                        choices=PAYMENT_OPTION)


class UpdateAddressForm(forms.Form):
    address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_or_suite = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment',
        'class': 'form-control'
    }))

    city = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'City',
        'class': 'form-control'
    }))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'custom-select d-block w-100'
    }))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    country = CountryField(blank_label='Select a country...').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        })
    )


class CreditCardForm(forms.Form):
    name_on_card = forms.CharField()

