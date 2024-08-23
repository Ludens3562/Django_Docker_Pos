from django.shortcuts import render
from .models import Product
from django.db.models import Sum
from django import forms


class ItemFilterForm(forms.Form):
    name = forms.CharField(required=False, label="商品名")
    price_min = forms.DecimalField(required=False, label="最低価格", min_value=0)
    price_max = forms.DecimalField(required=False, label="最高価格", min_value=0)
    tax_rate = forms.DecimalField(required=False, label="税率", min_value=0)
    stock_min = forms.IntegerField(required=False, label="最低在庫数", min_value=0)


def filter_items(request):
    form = ItemFilterForm(request.GET)
    products = Product.objects.all()

    if form.is_valid():
        # 商品名でフィルタリング
        if form.cleaned_data["name"]:
            products = products.filter(name__icontains=form.cleaned_data["name"])

        # 価格でフィルタリング
        if form.cleaned_data["price_min"] is not None:
            products = products.filter(price__gte=form.cleaned_data["price_min"])
        if form.cleaned_data["price_max"] is not None:
            products = products.filter(price__lte=form.cleaned_data["price_max"])

        # 軽減税率でフィルタリング
        if form.cleaned_data["tax_rate"] is not None:
            products = products.filter(tax_rate=form.cleaned_data["tax_rate"])

        # 在庫数でフィルタリング
        if form.cleaned_data["stock_min"] is not None:
            # 各商品に関連する在庫の合計を計算してフィルタリングする
            products = products.annotate(total_stock=Sum("stock__quantity")).filter(
                total_stock__gte=form.cleaned_data["stock_min"]
            )

    context = {
        "form": form,
        "products": products,
    }
    return render(request, "items/filter_items.html", context)
