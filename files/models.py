from django.conf import settings
from django.db import models

class DigitalFile(models.Model):
    class FileType(models.TextChoices):
        IMAGE = 'image', 'Image'
        MUSIC = 'music', 'Music'
        BOOK = 'book', 'Book'
        ARTICLE = 'article', 'Article'

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='digital_files'
    )
    type = models.CharField(max_length=10, choices=FileType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()  # مثلا تومان
    file = models.FileField(upload_to='uploads/files/')
    preview_image = models.ImageField(upload_to='uploads/previews/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.type}"


class ArticleDetail(models.Model):
    digital_file = models.OneToOneField(DigitalFile, on_delete=models.CASCADE, related_name='article_detail')
    keywords = models.CharField(max_length=255, blank=True)
    pages = models.PositiveIntegerField()

class BookDetail(models.Model):
    digital_file = models.OneToOneField(DigitalFile, on_delete=models.CASCADE, related_name='book_detail')
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True)
    pages = models.PositiveIntegerField()

class MusicDetail(models.Model):
    digital_file = models.OneToOneField(DigitalFile, on_delete=models.CASCADE, related_name='music_detail')
    artist = models.CharField(max_length=255, blank=True)
    duration_seconds = models.PositiveIntegerField()

class ImageDetail(models.Model):
    digital_file = models.OneToOneField(DigitalFile, on_delete=models.CASCADE, related_name='image_detail')
    resolution = models.CharField(max_length=50, blank=True)  # مثلا 1920x1080
    format = models.CharField(max_length=10, blank=True)      # png/jpg
