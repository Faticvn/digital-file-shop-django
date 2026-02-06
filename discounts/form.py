from django import forms
from .models import DiscountCode

class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = ["code", "discount_type", "value", "start_at", "end_at", "max_uses", "is_active"]