from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created

def order_create(request):
    # pobranie koszyka
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        # sprawdzenie poprawności danych
        if form.is_valid():
            # tworzenia nowego zamówienia zapisać powiązany
            # z nim kupon i wysokość udzielonegorabatu.
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                # order item dla każdego produktu
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])
            # Usunięcie zawartości koszyka na zakupy.
            cart.clear()
            # Wysłanie asynchronicznego zadania po utworzeniu zamówienia.
            # Używamy metody delay() zadania w celu jego wywołania
            # w sposób asynchroniczny. Zadanie
            # będzie dodane do kolejki i wykonane przez wątek roboczy
            # tak wcześnie, jak to możliwe.
            order_created.delay(order.id)
            return render(request,
                              'orders/order/created.html',
                              {'order': order})
    # dla żądania GET
    else:
        form = OrderCreateForm()
    return render(request,'orders/order/create.html',
                            {'cart': cart, 'form': form})
