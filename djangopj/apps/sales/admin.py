from django.contrib import admin
from .models import SalesItem, Transaction


# SalesItemモデルの管理ページをカスタマイズ
class SalesItemAdmin(admin.ModelAdmin):
    list_display = ("name", "JAN", "price", "reduce_tax", "transaction")  # 一覧ページに表示するフィールド
    search_fields = ("name", "JAN")  # 検索フィールド


# Transactionモデルの管理ページをカスタマイズ
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "sales_type", "date", "total")  # 一覧ページに表示するフィールド
    search_fields = ("transaction_id",)  # 検索フィールド
    list_filter = ("sales_type", "date")  # フィルターに使うフィールド


# 管理サイトにモデルを登録
admin.site.register(SalesItem, SalesItemAdmin)
admin.site.register(Transaction, TransactionAdmin)
