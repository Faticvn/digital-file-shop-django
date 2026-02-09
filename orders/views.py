import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from discounts.models import DiscountCode
from files.models import DigitalFile
from notifications.services import send_purchase_email
from notifications.sms import send_sms
from .forms import CheckoutForm
from .models import Order, OrderItem

logger = logging.getLogger("shop")


def _get_cart(session):
    return session.get("cart", [])


def _set_cart(session, cart):
    session["cart"] = cart
    session.modified = True


def cart_add(request, file_id):
    if request.method == "POST":
        # فقط فایل‌های active
        f = get_object_or_404(DigitalFile.objects.active(), id=file_id)

        # جلوگیری از خرید فایل توسط فروشنده خودش
        if request.user.is_authenticated and getattr(request.user, "role", None) == "seller":
            if f.seller_id == request.user.id:
                messages.error(request, "شما نمی‌توانید فایل خودتان را به سبد خرید اضافه کنید.")
                logger.warning("CART_ADD_DENIED seller=%s file_id=%s", request.user.username, file_id)
                return redirect("files:file_detail", pk=f.id)

        cart = _get_cart(request.session)
        if file_id not in cart:
            cart.append(file_id)
        _set_cart(request.session, cart)

        logger.info("CART_ADD user=%s file_id=%s", getattr(request.user, "username", "anon"), file_id)

    return redirect("orders:cart")


def cart_remove(request, file_id):
    if request.method == "POST":
        cart = _get_cart(request.session)
        if file_id in cart:
            cart.remove(file_id)
        _set_cart(request.session, cart)

        logger.info("CART_REMOVE user=%s file_id=%s", getattr(request.user, "username", "anon"), file_id)

    return redirect("orders:cart")


def cart_view(request):
    cart_ids = _get_cart(request.session)

    # فقط فایل‌های active
    items = list(DigitalFile.objects.active().filter(id__in=cart_ids))
    total = sum(i.price for i in items)

    return render(request, "orders/cart.html", {"items": items, "total": total})


def _validate_discount(code: str, items):
    """
    قوانین:
    - کد باید متعلق به فروشنده فایل‌های داخل سبد باشد
    - فعّال باشد
    - زمان start_at/end_at رعایت شود
    - max_uses == 0 یعنی نامحدود
    """
    code = (code or "").strip()
    if not code:
        return None, "کد تخفیف وارد نشده است."

    if not items:
        return None, "سبد خرید خالی است."

    sellers = {it.seller_id for it in items}
    if len(sellers) != 1:
        return None, "کد تخفیف فقط برای سبد خریدِ تک‌فروشنده قابل استفاده است."

    seller_id = next(iter(sellers))

    discount = DiscountCode.objects.filter(
        code=code,
        seller_id=seller_id,
        is_active=True,
    ).first()

    if not discount:
        return None, "کد تخفیف معتبر نیست یا متعلق به این فروشنده نیست."

    now = timezone.now()

    if discount.start_at and discount.start_at > now:
        return None, "زمان استفاده از این کد تخفیف هنوز شروع نشده است."

    if discount.end_at and discount.end_at < now:
        return None, "این کد تخفیف منقضی شده است."

    # max_uses == 0 یعنی نامحدود
    if discount.max_uses and discount.used_count >= discount.max_uses:
        return None, "ظرفیت استفاده از این کد تخفیف تمام شده است."

    return discount, None


@login_required
def checkout(request):
    from notifications.sms import send_sms  # اضافه کردن import داخل تابع

    cart_ids = _get_cart(request.session)
    items = list(DigitalFile.objects.filter(id__in=cart_ids, is_active=True))

    if not items:
        messages.info(request, "سبد خرید خالی است.")
        return redirect("files:file_list")

    total = sum(i.price for i in items)
    form = CheckoutForm(request.POST or None)
    discount_obj = None
    discount_amount = 0
    final_total = total

    # محاسبه تخفیف اگر کد معتبر باشد
    if form.is_valid():
        code = (form.cleaned_data.get("discount_code") or "").strip()
        if code:
            discount_obj = DiscountCode.objects.filter(code=code, is_active=True).first()

            if discount_obj:
                today = timezone.now().date()
                if discount_obj.start_date and discount_obj.start_date > today:
                    discount_obj = None
                if discount_obj and discount_obj.end_date and discount_obj.end_date < today:
                    discount_obj = None

            if discount_obj:
                if discount_obj.max_uses is not None and discount_obj.used_count >= discount_obj.max_uses:
                    discount_obj = None

            if discount_obj:
                if discount_obj.discount_type == "percent":
                    discount_amount = (total * discount_obj.value) // 100
                else:
                    discount_amount = discount_obj.value

                discount_amount = min(discount_amount, total)
                final_total = total - discount_amount

    if request.method == "POST":
        if not form.is_valid():
            return render(request, "orders/checkout.html", {
                "items": items,
                "total": total,
                "final_total": final_total,
                "discount_amount": discount_amount,
                "discount_error": discount_error,
                "form": form,
            })

        order = Order.objects.create(
            buyer=request.user,
            status=Order.Status.PAID,
            total_price=final_total,
            paid_at=timezone.now(),
        )

        for f in items:
            OrderItem.objects.create(
                order=order,
                digital_file=f,
                seller=f.seller,
                price_at_purchase=f.price,
            )

        # ارسال پیامک به خریدار
        send_sms(
            request.user.phone,
            f"خرید شما با موفقیت انجام شد. شماره سفارش: {order.id}"
        )

        # ارسال پیامک به فروشندگان
        seller_ids = set(order.items.values_list("seller_id", flat=True))
        for sid in seller_ids:
            seller_user = User.objects.filter(id=sid).first()
            if seller_user and seller_user.phone:
                send_sms(
                    seller_user.phone,
                    f"یک خرید جدید برای فایل‌های شما ثبت شد. شماره سفارش: {order.id}"
                )

        if discount_obj:
            discount_obj.used_count += 1
            discount_obj.save(update_fields=["used_count"])

        logger.info(
            "CHECKOUT paid buyer=%s order_id=%s total=%s items=%s",
            request.user.username,
            order.id,
            order.total_price,
            len(items),
        )

        # ایمیل (امتیازی)
        send_purchase_email(
            to_email=request.user.email,
            subject="خرید موفق - فروش فایل دیجیتال",
            message=(
                f"سلام {request.user.username}\n\n"
                f"خرید شما با موفقیت انجام شد.\n"
                f"شماره سفارش: {order.id}\n"
                f"مبلغ پرداختی: {order.total_price}\n\n"
                f"برای دانلود فایل‌ها وارد بخش «دانلودهای من» شوید."
            ),
        )

        _set_cart(request.session, [])
        messages.success(request, "خرید با موفقیت انجام شد.")
        return redirect("orders:my_downloads")

    return render(
        request,
        "orders/checkout.html",
        {
            "items": items,
            "total": total,
            "final_total": final_total,
            "discount_amount": discount_amount,
            "discount_error": discount_error,
            "form": form,
        },
    )

@login_required
def my_downloads(request):
    paid_items = (
        OrderItem.objects.filter(
            order__buyer=request.user,
            order__status=Order.Status.PAID,
        )
        .select_related("digital_file")
        .order_by("-id")
    )

    files = [it.digital_file for it in paid_items]
    return render(request, "orders/my_downloads.html", {"files": files})


@login_required
def download_file(request, file_id):
    has_access = OrderItem.objects.filter(
        order__buyer=request.user,
        order__status=Order.Status.PAID,
        digital_file_id=file_id,
    ).exists()

    if not has_access:
        logger.warning("DOWNLOAD_DENIED user=%s file_id=%s", request.user.username, file_id)
        raise Http404("شما به این فایل دسترسی ندارید.")

    # فقط فایل‌های active
    f = get_object_or_404(DigitalFile.objects.active(), id=file_id)

    if not f.file:
        raise Http404("فایل موجود نیست.")

    logger.info("DOWNLOAD_OK user=%s file_id=%s", request.user.username, file_id)

    return FileResponse(
        f.file.open("rb"),
        as_attachment=True,
        filename=f.file.name.split("/")[-1],
    )