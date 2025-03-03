from django.db import models
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta,datetime

# Create your models here.

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    content = models.TextField()
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_products')

    price = models.IntegerField()
    discount_rate = models.IntegerField(default=0)
    discounted_price = models.IntegerField()

    category_Choices = (('전체상품','전체상품') ,('전통주','전통주'), ('맥주','맥주'), ('위스키','위스키'), ('와인','와인'))
    category = models.CharField(max_length=20, choices=category_Choices)

    alcohol_percentage = models.IntegerField()

    sweetness_Choices = (('약한','약한') ,('중간','중간'), ('강한','강한'))
    sweetness = models.CharField(max_length=20, choices=sweetness_Choices)

    sourness_Choices = (('약한','약한') ,('중간','중간'), ('강한','강한'))
    sourness = models.CharField(max_length=20, choices=sourness_Choices)

    bitterness_Choices = (('약한','약한') ,('중간','중간'), ('강한','강한'))
    bitterness = models.CharField(max_length=20, choices=bitterness_Choices)

    carbonated = models.BooleanField()

    volume = models.IntegerField()

    delivery_date = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def product_image_path(instance, filename):
        return f'products/{instance.pk}/{filename}'
    
    image = ProcessedImageField(
        upload_to=product_image_path,
        processors=[ResizeToFill(320,426)],
        format='JPEG',
        options={'quality' : 100},
        blank=True,
        null=True,
    )

    def calculate_discount_price(self):
        return round((self.price * (1 -self.discount_rate / 100)) / 10) * 10
    
    def save(self,*args, **kargs):
        self.discounted_price = self.calculate_discount_price()
        super().save(*args, **kargs)

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def comment_image_path(instance, filename):
        return f'products/{instance.pk}/{filename}'

    image = ProcessedImageField(
        upload_to=comment_image_path,
        processors=[ResizeToFill(100,100)],
        format='JPEG',
        options={'quality' : 100},
        blank=True,
        null=True,
    )

    star = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])

    @property
    def created_string(self):
        time = datetime.now(tz=timezone.utc) - self.created_at

        if time < timedelta(minutes=1):
            return '방금 전'
        elif time < timedelta(hours=1):
            return str(int(time.seconds / 60)) + '분 전'
        elif time < timedelta(days=1):
            return str(int(time.seconds / 3600)) + '시간 전'
        elif time < timedelta(days=7):
            time = datetime.now(tz=timezone.utc).date() - self.created_at.date()
            return str(time.days) + '일 전'
        else:
            return self.strftime('%Y-%m-%d')
