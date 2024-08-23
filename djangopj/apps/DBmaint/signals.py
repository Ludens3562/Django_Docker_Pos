from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, Stock, Store
from django.db import transaction


# 商品が追加されたら、全店舗分の在庫リストを作成
@receiver(post_save, sender=Product)
def create_stock_for_new_product(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            stores = Store.objects.all()
            for store in stores:
                # StorecodeとJANの組み合わせが存在しない場合にのみ作成
                if not Stock.objects.filter(storecode=store, JAN=instance).exists():
                    Stock.objects.create(storecode=store, JAN=instance, quantity=0)


# 店舗が追加されたら、全商品分の在庫リストを作成
@receiver(post_save, sender=Store)
def create_stock_for_new_store(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            products = Product.objects.all()
            for product in products:
                # StorecodeとJANの組み合わせが存在しない場合にのみ作成
                if not Stock.objects.filter(storecode=instance, JAN=product).exists():
                    Stock.objects.create(storecode=instance, JAN=product, quantity=0)
