import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib import messages

from .forms import SignupForm
from .services import send_verification_email, verify_user

logger = logging.getLogger("shop")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # بعد از ثبت نام هنوز تایید نشده
            user.is_verified = False
            user.save()

            login(request, user)

            # ارسال ایمیل تایید (تو ترمینال چاپ میشه چون console backend داری)
            send_verification_email(request, user)

            logger.info("SIGNUP user=%s role=%s", user.username, getattr(user, "role", None))
            messages.info(request, "ثبت‌نام انجام شد. لینک تایید ایمیل در کنسول چاپ شد.")
            return redirect("files:file_list")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


def verify_email(request, uidb64, token):
    user = verify_user(uidb64, token)
    if user:
        messages.success(request, "ایمیل با موفقیت تایید شد ✅")
        logger.info("EMAIL_VERIFIED user=%s", user.username)
    else:
        messages.error(request, "لینک تایید نامعتبر یا منقضی شده است.")
        logger.warning("EMAIL_VERIFY_FAILED uid=%s", uidb64)

    return redirect("files:file_list")


def login_view(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            logger.info("LOGIN success user=%s", user.username)
            return redirect("files:file_list")

        logger.warning("LOGIN failed username=%s", username)
        return render(request, "accounts/login.html", {"error": "نام کاربری یا رمز اشتباه است"})

    return render(request, "accounts/login.html")


def logout_view(request):
    if request.user.is_authenticated:
        logger.info("LOGOUT user=%s", request.user.username)
    logout(request)
    return redirect("files:file_list")