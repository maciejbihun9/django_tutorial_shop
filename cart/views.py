from django.shortcuts import render

# Create your views here.
# CART VIEWS
# dodanie produktu do koszykna na zakupy,
# NIE następuje zapisanie do bazy danych,
# po takich akcjach zwykle następuje przekierowanie do jakiegoś widoku,
# bo te akcje nie posiadają swojego dedykowanego widoku.
from cart.cart import Cart
from cart.forms import CartAddProductForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from shop.recommender import Recommender
from coupons.forms import CouponApplyForm
import web_pdb

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
            quantity=cd['quantity'],
            update_quantity=cd['update'])
    return redirect('cart:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        # dodaj do dict każdego elementu podane pole
        # czyli teraz dict posiada pole formy, którą można wyświetlić w widoku
        # tutaj nie ma przesyłania formy!
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'],
                     'update': True})
    coupon_apply_form = CouponApplyForm()
    r = Recommender()
    cart_products = [item['product'] for item in cart]
    recommended_products = r.suggest_products_for(cart_products,
                                                  max_results=4)
    # web_pdb.set_trace()
    return render(request, 'cart/detail.html',
                  {'cart': cart,
                   'coupon_apply_form': coupon_apply_form,
                   'recommended_products': recommended_products})