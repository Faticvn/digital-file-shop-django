from django import forms
from .models import DigitalFile, ArticleDetail, BookDetail, MusicDetail, ImageDetail

class DigitalFileForm(forms.ModelForm):
    class Meta:
        model = DigitalFile
        fields = ["type", "title", "description", "price", "file", "preview_image", "is_active"]

class ArticleDetailForm(forms.ModelForm):
    class Meta:
        model = ArticleDetail
        fields = ["keywords", "pages"]

class BookDetailForm(forms.ModelForm):
    class Meta:
        model = BookDetail
        fields = ["author", "isbn", "pages"]

class MusicDetailForm(forms.ModelForm):
    class Meta:
        model = MusicDetail
        fields = ["artist", "duration_seconds"]

class ImageDetailForm(forms.ModelForm):
    class Meta:
        model = ImageDetail
        fields = ["resolution", "format"]