from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone

from files.models import DigitalFile, ArticleDetail, BookDetail, MusicDetail, ImageDetail
from discounts.models import DiscountCode


class Command(BaseCommand):
    help = "Seed test data for Digital File Shop"

    def handle(self, *args, **options):
        User = get_user_model()

        # --- users ---
        seller1, _ = User.objects.get_or_create(username="seller1", defaults={"role": "seller"})
        seller1.set_password("12345678")
        seller1.save()

        seller2, _ = User.objects.get_or_create(username="seller2", defaults={"role": "seller"})
        seller2.set_password("12345678")
        seller2.save()

        buyer1, _ = User.objects.get_or_create(username="buyer1", defaults={"role": "buyer"})
        buyer1.set_password("12345678")
        buyer1.save()

        buyer2, _ = User.objects.get_or_create(username="buyer2", defaults={"role": "buyer"})
        buyer2.set_password("12345678")
        buyer2.save()

        def fake_file(name: str):
            return ContentFile(b"demo content", name=name)

        # --- files ---
        if not DigitalFile.objects.exists():
            a = DigitalFile.objects.create(
                seller=seller1,
                type="article",
                title="مقاله تستی ۱",
                description="یک مقاله تستی برای ارائه",
                price=10000,
                file=fake_file("article1.txt"),
                is_active=True,
            )
            ArticleDetail.objects.create(digital_file=a, keywords="django,web", pages=12)

            b = DigitalFile.objects.create(
                seller=seller1,
                type="book",
                title="کتاب تستی ۱",
                description="یک کتاب تستی برای ارائه",
                price=25000,
                file=fake_file("book1.txt"),
                is_active=True,
            )
            BookDetail.objects.create(digital_file=b, author="نویسنده تست", isbn="123456", pages=150)

            m = DigitalFile.objects.create(
                seller=seller2,
                type="music",
                title="موسیقی تستی ۱",
                description="یک موسیقی تستی",
                price=15000,
                file=fake_file("music1.txt"),
                is_active=True,
            )
            MusicDetail.objects.create(digital_file=m, artist="Artist", duration_seconds=210)

            img = DigitalFile.objects.create(
                seller=seller2,
                type="image",
                title="تصویر تستی ۱",
                description="یک تصویر تستی",
                price=8000,
                file=fake_file("image1.txt"),
                is_active=True,
            )
            ImageDetail.objects.create(digital_file=img, resolution="1920x1080", format="jpg")

        # --- discounts ---
        now = timezone.now()

        DiscountCode.objects.get_or_create(
            seller=seller1,
            code="OFF10",
            defaults={
                "discount_type": "percent",
                "value": 10,
                "start_at": now,
                "end_at": None,
                "max_uses": 0,  # نامحدود
                "used_count": 0,
                "is_active": True,
            },
        )

        DiscountCode.objects.get_or_create(
            seller=seller2,
            code="OFF5000",
            defaults={
                "discount_type": "fixed",
                "value": 5000,
                "start_at": now,
                "end_at": None,
                "max_uses": 5,
                "used_count": 0,
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("✅ Seed completed!"))
        self.stdout.write("Users: seller1/seller2/buyer1/buyer2  (password: 12345678)")
        self.stdout.write("Discounts: OFF10 (seller1) , OFF5000 (seller2)")