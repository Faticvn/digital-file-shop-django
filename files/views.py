import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    ArticleDetailForm,
    BookDetailForm,
    DigitalFileForm,
    ImageDetailForm,
    MusicDetailForm,
)
from .models import DigitalFile

logger = logging.getLogger("shop")


def file_list(request):
    qs = DigitalFile.objects.active()

    file_type = (request.GET.get("type") or "").strip()
    q = (request.GET.get("q") or "").strip()

    if file_type:
        qs = qs.filter(type=file_type)

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    qs = qs.order_by("-id")
    return render(request, "files/list.html", {"files": qs, "q": q, "type": file_type})


def file_detail(request, pk):
    f = get_object_or_404(DigitalFile.objects.active(), pk=pk)
    return render(request, "files/detail.html", {"file": f})


@login_required
def file_create(request):
    if getattr(request.user, "role", None) != "seller":
        messages.error(request, "فقط فروشنده می‌تواند فایل ثبت کند.")
        return redirect("files:file_list")


    article_form = ArticleDetailForm(prefix="article")
    book_form = BookDetailForm(prefix="book")
    music_form = MusicDetailForm(prefix="music")
    image_form = ImageDetailForm(prefix="image")

    detail_form = None

    if request.method == "POST":
        form = DigitalFileForm(request.POST, request.FILES)
        selected_type = request.POST.get("type")

        if selected_type == "article":
            article_form = ArticleDetailForm(request.POST, prefix="article")
            detail_form = article_form
        elif selected_type == "book":
            book_form = BookDetailForm(request.POST, prefix="book")
            detail_form = book_form
        elif selected_type == "music":
            music_form = MusicDetailForm(request.POST, prefix="music")
            detail_form = music_form
        elif selected_type == "image":
            image_form = ImageDetailForm(request.POST, prefix="image")
            detail_form = image_form

        main_ok = form.is_valid()
        detail_ok = (detail_form.is_valid() if detail_form else False)

        if main_ok and detail_ok:
            digital_file = form.save(commit=False)
            digital_file.seller = request.user
            digital_file.save()

            detail_obj = detail_form.save(commit=False)
            detail_obj.digital_file = digital_file
            detail_obj.save()

            logger.info(
                "FILE_CREATE seller=%s file_id=%s type=%s title=%s price=%s",
                request.user.username,
                digital_file.id,
                digital_file.type,
                digital_file.title,
                digital_file.price,
            )

            messages.success(request, "فایل ثبت شد.")
            return redirect("files:file_detail", pk=digital_file.pk)

    else:
        form = DigitalFileForm()

    return render(
        request,
        "files/create.html",
        {
            "form": form,
            "detail_form": detail_form,
            "article_form": article_form,
            "book_form": book_form,
            "music_form": music_form,
            "image_form": image_form,
        },
    )