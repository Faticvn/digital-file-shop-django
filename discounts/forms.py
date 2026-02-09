from django import forms
from .models import DiscountCode


class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name in ("seller", "used_count"):
            if name in self.fields:
                self.fields.pop(name)

    def clean_code(self):
        code = (self.cleaned_data.get("code") or "").strip()
        return code.upper()