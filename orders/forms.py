from django import forms

class CheckoutForm(forms.Form):
    discount_code = forms.CharField(required=False, max_length=50, label="کد تخفیف")