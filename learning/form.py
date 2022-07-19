from django import forms
from .models import New_subscriber, User, Coupon, subscribe_class
from django.contrib.auth.forms import UserCreationForm
from django_countries.widgets import CountrySelectWidget


class SubscribersForm(forms.ModelForm):
    email = forms.EmailField(label='email',
                             widget=forms.EmailInput(
                                 attrs={
                                     'placeholder': "Enter your email",
                                     'class': '',
                                     'id': ''
                                
                                 }
                             )
                             )

    class Meta:
        model = New_subscriber
        fields = ['email']

class ClassSubscribersForm(forms.ModelForm):
    name = forms.CharField(label='Name',
                             widget=forms.TextInput(
                                 attrs={
                                     'class': 'form-control',
                                     'id': 'form5Example1',
                                     'value':'{{request.user}}',
                                 }
                             )
                             )

    email = forms.EmailField(label='Email address',
                             widget=forms.EmailInput(
                                 attrs={
                                     'class': 'form-control',
                                     'id': 'form5Example2'
                                 }
                             )
                             )

    class Meta:
        model = subscribe_class
        fields = ['name', 'email']


class CustomUserForm(UserCreationForm):
    username = forms.CharField(label='',
                               widget=forms.TextInput(
                                   attrs={
                                     'placeholder': "Username",
                                     'class': 'form-control',
                                     'id': 'inputName'
                                   }
                               )
                               )
    email = forms.EmailField(label='',
                             widget=forms.EmailInput(
                                   attrs={
                                       'placeholder': "Email Address",
                                       'class': 'form-control',
                                       'id': 'inputEmail'
                                   }
                             )
                             )
    password1 = forms.CharField(label='',
                                widget=forms.PasswordInput(
                                    attrs={
                                        'placeholder': "Password",
                                        'class': 'form-control',
                                        'id': 'inputPassword'
                                    }
                                )
                                )
    password2 = forms.CharField(label='',
                                widget=forms.PasswordInput(
                                    attrs={
                                        'placeholder': "Confirm Password",
                                        'class': 'form-control',
                                        'id': 'inputPassword'
                                    }
                                )
                                )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CouponForm(forms.Form):
    code = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2',
        'name': 'codes'
    }))
    class Meta:
        model = Coupon
        fields = ['code']
# class OrderForm(forms.ModelsForm):
#     class Meta:
#         models = Payed_class
#         fields = ('country')
#         widgets = {'country': CountrySelectWidget()}