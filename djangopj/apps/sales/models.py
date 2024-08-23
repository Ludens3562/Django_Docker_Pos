<<<<<<< HEAD
from django.db import models


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    sales_type = models.IntegerField()
    date = models.DateTimeField(auto_now=True)
    staffCode = models.IntegerField()
    purchase_points = models.IntegerField()
    tax = models.IntegerField()
    red_tax = models.IntegerField()
    total = models.IntegerField()
    deposit = models.IntegerField()
    change = models.IntegerField()

    def __str__(self):
        return str(self.transaction_id)


class SalesItem(models.Model):
    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, related_name="sales_items")  # 関連名を修正
    JAN = models.CharField(max_length=13)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    reduce_tax = models.BooleanField(default=False)

    def __str__(self):
        return self.name
=======
from django.db import models
>>>>>>> 230bdf6162403665a2b8d8e5928dd09a76e9a537
