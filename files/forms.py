from django import forms
from .models import DigitalFile, ArticleDetail, BookDetail, MusicDetail, ImageDetail


class DigitalFileForm(forms.ModelForm):
    class Meta:
        model = DigitalFile
        fields = ["title", "description", "type", "price", "file", "is_active"]


class ArticleDetailForm(forms.ModelForm):
    class Meta:
        model = ArticleDetail
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if "digital_file" in self.fields:
            self.fields.pop("digital_file")


class BookDetailForm(forms.ModelForm):
    class Meta:
        model = BookDetail
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "digital_file" in self.fields:
            self.fields.pop("digital_file")


class MusicDetailForm(forms.ModelForm):
    class Meta:
        model = MusicDetail
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "digital_file" in self.fields:
            self.fields.pop("digital_file")


class ImageDetailForm(forms.ModelForm):
    class Meta:
        model = ImageDetail
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "digital_file" in self.fields:
            self.fields.pop("digital_file")