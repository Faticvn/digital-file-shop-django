from django.contrib import admin
from .models import DigitalFile, ArticleDetail, BookDetail, MusicDetail, ImageDetail

admin.site.register(DigitalFile)
admin.site.register(ArticleDetail)
admin.site.register(BookDetail)
admin.site.register(MusicDetail)
admin.site.register(ImageDetail)
