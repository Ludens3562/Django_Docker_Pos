import requests
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product, Transaction
from .forms import ItemFilterForm
from django.contrib.auth.decorators import login_required
from .get_recept_data import generate_receipt_text


def filter_products(request):
    products = Product.objects.all()
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
        if form.cleaned_data["stock_min"] is not None:
            products = products.filter(total_stock__gte=form.cleaned_data["stock_min"])

    context = {"form": form, "items": products}
    return render(request, "app/filter_items.html", context)


@login_required
def generate_receipt_view(request, sale_id):
    try:
        # Transactionオブジェクトの取得
        transaction = get_object_or_404(Transaction, sale_id=sale_id)

        # レシートテキストの生成をサービス層に委譲
        receipt_text = generate_receipt_text(transaction)

        # レシートデータをPOSTリクエストで送信
        response = requests.post("http://receipt:6573/generate", data={"text": receipt_text})
        if response.status_code == 200:
            # HTMLコンテンツを取得してそのままレスポンスとして返す
            html_content = response.text
            return HttpResponse(html_content, content_type="text/html; charset=utf-8")
        else:
            return HttpResponse("Failed to generate receipt.", content_type="text/plain")

    except Transaction.DoesNotExist:
        return HttpResponse("Transaction not found.", content_type="text/plain")