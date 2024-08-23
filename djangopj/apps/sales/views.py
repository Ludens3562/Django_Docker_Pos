from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.db import transaction
from apps.DBmaint.models import Product, Stock  # 'DBmaint.models'からのインポートを変更


# アイテム一覧を取得して、JANコード、商品名、価格を多次元リストに保存する関数
def get_items_and_data(item_list):
    items_in_cart = []
    for jan in item_list:
        product_obj = Product.objects.filter(JAN=jan).first()
        if product_obj:
            items_in_cart.append([product_obj.JAN, product_obj.name, product_obj.tax, product_obj.price])
    return items_in_cart


# テンプレートに変数を渡すための共通関数
def render_items_template(request, template_name):
    item_list = request.session.get("item_list", [])
    items_data = get_items_and_data(item_list)
    total_price = sum(item[3] for item in items_data)  # 合計金額の計算
    return render(request, template_name, {"items_data": items_data, "total_price": total_price})


@require_http_methods(["GET", "POST"])
def add_item_to_list(request):
    if request.method == "POST":
        jan_code = request.POST.get("jan", "")
        product_instance = Product.objects.filter(JAN=jan_code).first()

        if product_instance:
            if "item_list" not in request.session or not request.session["item_list"]:
                request.session["item_list"] = []
            item_list = request.session["item_list"]

            item_list.append(product_instance.JAN)
            request.session["item_list"] = item_list

            return redirect("../add_item/")
        else:
            return render(request, "add_item.html", {"error": "商品が見つかりません。"})
    else:
        return render_items_template(request, "add_item.html")


@require_http_methods(["POST"])
def delete_item_from_list(request):
    jan_code = request.POST.get("jan", "")
    if "item_list" in request.session:
        try:
            item_list = request.session["item_list"]
            item_list.remove(jan_code)
            request.session["item_list"] = item_list
        except ValueError:
            pass
    return redirect("../add_item/")


@transaction.atomic
def proceed_to_checkout(request):
    if "item_list" in request.session:
        item_list = request.session["item_list"]

        for jan in item_list:
            stock_instance = Stock.objects.filter(JAN__JAN=jan).first()
            if stock_instance and stock_instance.quantity > 0:
                stock_instance.quantity -= 1
                stock_instance.save()

        del request.session["item_list"]

    return redirect("../add_item/")
