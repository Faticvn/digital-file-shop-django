from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import DigitalFile

def file_list(request):
    qs = DigitalFile.objects.filter(is_active=True)

    file_type = request.GET.get('type')
    q = request.GET.get('q')

    if file_type:
        qs = qs.filter(type=file_type)

    if q:
        qs = qs.filter(Q(titleicontains=q) | Q(descriptionicontains=q))

    context = {
        'files': qs.order_by('-created_at'),
        'selected_type': file_type or '',
        'q': q or '',
        'types': DigitalFile.FileType.choices,
    }
    return render(request, 'files/list.html', context)

def file_detail(request, pk):
    obj = get_object_or_404(DigitalFile, pk=pk, is_active=True)
    return render(request, 'files/detail.html', {'file': obj})


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .forms import (
    DigitalFileForm, ArticleDetailForm, BookDetailForm, MusicDetailForm, ImageDetailForm
)

@login_required
def file_create(request):
    if request.user.role != 'seller':
        return HttpResponseForbidden("فقط فروشنده می‌تواند فایل ثبت کند.")

    if request.method == "POST":
        form = DigitalFileForm(request.POST, request.FILES)

        # فرم جزئیات را بر اساس type می‌سازیم
        detail_type = request.POST.get("type")
        detail_form = None
        if detail_type == "article":
            detail_form = ArticleDetailForm(request.POST)
        elif detail_type == "book":
            detail_form = BookDetailForm(request.POST)
        elif detail_type == "music":
            detail_form = MusicDetailForm(request.POST)
        elif detail_type == "image":
            detail_form = ImageDetailForm(request.POST)

        if form.is_valid() and (detail_form is None or detail_form.is_valid()):
            obj = form.save(commit=False)
            obj.seller = request.user
            obj.save()

            if detail_form:
                d = detail_form.save(commit=False)
                d.digital_file = obj
                d.save()

            return redirect("files:detail", pk=obj.pk)
    else:
        form = DigitalFileForm()
        detail_form = None

    return render(request, "files/create.html", {"form": form, "detail_form": detail_form})