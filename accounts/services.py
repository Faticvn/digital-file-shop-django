from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    url = request.build_absolute_uri(
        reverse("accounts:verify_email", kwargs={"uidb64": uid, "token": token})
    )

    subject = "تایید ایمیل - فروش فایل دیجیتال"
    message = f"سلام {user.username}\n\nبرای تایید ایمیل روی لینک زیر کلیک کن:\n{url}\n"

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
        recipient_list=[user.email] if user.email else [],
        fail_silently=True,
    )


def verify_user(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return None

    if default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        return user

    return None