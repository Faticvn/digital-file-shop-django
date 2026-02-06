from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from .forms import DiscountCodeForm

@login_required
def discount_create(request):
    if request.user.role != "seller":
        return HttpResponseForbidden("فقط فروشنده می‌تواند کد تخفیف بسازد.")

    if request.method == "POST":
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.seller = request.user
            obj.save()
            return redirect("files:list")
    else:
        form = DiscountCodeForm()

    return render(request, "discounts/create.html", {"form": form})