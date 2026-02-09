import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import DiscountCodeForm

logger = logging.getLogger("shop")


@login_required
def discount_create(request):
    if getattr(request.user, "role", None) != "seller":
        messages.error(request, "فقط فروشنده می‌تواند کد تخفیف بسازد.")
        return redirect("files:file_list")

    if request.method == "POST":
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            # seller باید از کاربر لاگین گرفته شود
            obj.seller = request.user

            obj.save()

            logger.info(
                "DISCOUNT_CREATE seller=%s code=%s type=%s value=%s max_uses=%s",
                request.user.username,
                obj.code,
                obj.discount_type,
                obj.value,
                obj.max_uses,
            )

            messages.success(request, "کد تخفیف ساخته شد.")
            return redirect("discounts:create")
    else:
        form = DiscountCodeForm()

    return render(request, "discounts/create.html", {"form": form})