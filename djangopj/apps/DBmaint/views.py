from django.shortcuts import render
from django.db.models import Sum
from .models import Product, Stock
from .forms import ItemFilterForm


def filter_products(request):
    # Productモデルからすべての商品を取得
    products = Product.objects.all()

    # 在庫数を集計するために、ProductモデルとStockモデルを結びつける
    products = products.annotate(total_stock=Sum("stock__quantity"))

    form = ItemFilterForm(request.GET or None)

    if form.is_valid() and request.GET:
        if form.cleaned_data["name"]:
            products = products.filter(name__icontains=form.cleaned_data["name"])
        if form.cleaned_data["price_min"] is not None:
            products = products.filter(price__gte=form.cleaned_data["price_min"])
        if form.cleaned_data["price_max"] is not None:
            products = products.filter(price__lte=form.cleaned_data["price_max"])
        if form.cleaned_data["tax_rate"] is not None:
            products = products.filter(tax=form.cleaned_data["tax_rate"])
        # 在庫数でフィルタリング
        if form.cleaned_data["stock_min"] is not None:
            products = products.filter(total_stock__gte=form.cleaned_data["stock_min"])

    context = {"form": form, "items": items}
    return render(request, "app/filter_items.html", context)
