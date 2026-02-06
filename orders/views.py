from django.shortcuts import redirect, render
from django.utils import timezone
from files.models import DigitalFile
from .models import Order, OrderItem

def _get_cart(session):
    return session.get('cart', [])

def cart_add(request, file_id):
    if request.method == 'POST':
        cart = _get_cart(request.session)
        if file_id not in cart:
            cart.append(file_id)
        request.session['cart'] = cart
    return redirect('orders:cart')

def cart_view(request):
    cart_ids = _get_cart(request.session)
    items = DigitalFile.objects.filter(id__in=cart_ids)
    total = sum(i.price for i in items)
    return render(request, 'orders/cart.html', {'items': items, 'total': total})

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    cart_ids = _get_cart(request.session)
    items = list(DigitalFile.objects.filter(id__in=cart_ids, is_active=True))

    total = sum(i.price for i in items)

    if request.method == 'POST':
        order = Order.objects.create(
            buyer=request.user,
            status=Order.Status.PAID,
            total_price=total,
            paid_at=timezone.now()
        )
        for f in items:
            OrderItem.objects.create(
                order=order,
                digital_file=f,
                seller=f.seller,
                price_at_purchase=f.price
            )
        request.session['cart'] = []
        return redirect('files:list')

    return render(request, 'orders/checkout.html', {'items': items, 'total': total})